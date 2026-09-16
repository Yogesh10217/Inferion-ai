"""Immutable Agent Execution Traces Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import (
    CrossTenantAgentAccessException,
    ImmutableAgentExecutionException,
)
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.platform_contracts.snapshots import SnapshotFactory
from app.platform_contracts.tenant import TenantAccessGuard


class TraceStatus(str, Enum):
    RECORDING = "RECORDING"
    FINALIZED = "FINALIZED"
    VERIFIED = "VERIFIED"
    CORRUPTED = "CORRUPTED"


class TraceEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"tevent_{uuid.uuid4().hex[:10]}")
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details_sanitized: Dict[str, Any] = Field(default_factory=dict)


class AgentTraceStep(BaseModel):
    step_number: int
    action_type: str
    governance_decision_id: Optional[str] = None
    tool_invocation_id: Optional[str] = None
    delegation_id: Optional[str] = None
    outcome_summary: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TraceReference(BaseModel):
    trace_id: str
    tenant_id: str
    fingerprint: str
    snapshot_id: str


class AgentTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    plan_id: Optional[str] = None
    execution_id: Optional[str] = None
    status: TraceStatus = TraceStatus.RECORDING
    steps: List[AgentTraceStep] = Field(default_factory=list)
    events: List[TraceEvent] = Field(default_factory=list)
    fingerprint: str = ""
    snapshot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None


class AgentTraceManager:
    """Manages sanitized execution trace logs and finalizes immutable SHA-256 fingerprinted PlatformSnapshots."""

    def __init__(
        self,
        sanitizer: Optional[SensitiveDataSanitizer] = None,
        snapshot_factory: Optional[SnapshotFactory] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.sanitizer = sanitizer or SensitiveDataSanitizer()
        self.snapshot_factory = snapshot_factory or SnapshotFactory()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._traces: Dict[str, AgentTrace] = {}

    def start_trace(
        self,
        tenant_id: str,
        agent_id: str,
        task_id: str,
        plan_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> AgentTrace:
        tid = trace_id or f"trace_{uuid.uuid4().hex[:12]}"
        trace = AgentTrace(
            trace_id=tid,
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task_id,
            plan_id=plan_id,
            execution_id=execution_id,
            status=TraceStatus.RECORDING,
        )
        self._traces[trace.trace_id] = trace
        return trace

    def get_trace(self, trace_id: str, tenant_id: str) -> AgentTrace:
        trace = self._traces.get(trace_id)
        if not trace:
            # Return blank trace fallback
            return AgentTrace(trace_id=trace_id, tenant_id=tenant_id, agent_id="unknown", task_id="unknown")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, trace.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, trace.tenant_id)

        return trace

    def record_step(
        self,
        trace_id: str,
        tenant_id: str,
        action_type: str,
        governance_decision_id: Optional[str] = None,
        tool_invocation_id: Optional[str] = None,
        delegation_id: Optional[str] = None,
        outcome_summary: str = "",
        raw_event_details: Optional[Dict[str, Any]] = None,
    ) -> AgentTraceStep:
        trace = self.get_trace(trace_id, tenant_id)
        if trace.status == TraceStatus.FINALIZED:
            raise ImmutableAgentExecutionException(f"Trace '{trace_id}' is finalized and immutable.")

        step = AgentTraceStep(
            step_number=len(trace.steps) + 1,
            action_type=action_type,
            governance_decision_id=governance_decision_id,
            tool_invocation_id=tool_invocation_id,
            delegation_id=delegation_id,
            outcome_summary=outcome_summary,
        )
        trace.steps.append(step)

        if raw_event_details:
            sanitized = self.sanitizer.sanitize_copy(raw_event_details)
            ev = TraceEvent(
                event_type=action_type,
                details_sanitized=sanitized if isinstance(sanitized, dict) else {"data": str(sanitized)},
            )
            trace.events.append(ev)

        return step

    def finalize_trace(self, trace_id: str, tenant_id: str) -> AgentTrace:
        trace = self.get_trace(trace_id, tenant_id)
        if trace.status == TraceStatus.FINALIZED:
            return trace

        trace.status = TraceStatus.FINALIZED
        trace.finalized_at = datetime.now(timezone.utc)

        # Generate deterministic SHA-256 fingerprint
        payload_to_hash = {
            "trace_id": trace.trace_id,
            "tenant_id": trace.tenant_id,
            "agent_id": trace.agent_id,
            "task_id": trace.task_id,
            "steps": [s.model_dump() for s in trace.steps],
            "events": [e.model_dump() for e in trace.events],
            "finalized_at": trace.finalized_at.isoformat(),
        }
        fp = FingerprintGenerator.generate(payload_to_hash)
        trace.fingerprint = fp

        # Generate immutable PlatformSnapshot
        snap = self.snapshot_factory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="AGENT_TRACE",
            resource_id=trace.trace_id,
            domain_payload=payload_to_hash,
        )
        trace.snapshot_id = snap.metadata.snapshot_id

        return trace
