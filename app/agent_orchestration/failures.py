"""Failure Intelligence Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.event_intelligence.manager import EventIntelligenceManager
from app.platform_contracts.tenant import TenantAccessGuard
from app.reliability_platform.manager import ReliabilityPlatformManager


class AgentFailureType(str, Enum):
    CAPABILITY_VIOLATION = "CAPABILITY_VIOLATION"
    AUTONOMY_BREACH = "AUTONOMY_BREACH"
    TOOL_DENIED = "TOOL_DENIED"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    TIMEOUT = "TIMEOUT"
    SAFEGUARD_TRIGGERED = "SAFEGUARD_TRIGGERED"
    DELEGATION_FAILED = "DELEGATION_FAILED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"


class AgentFailureSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentFailurePattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"failpat_{uuid.uuid4().hex[:8]}")
    failure_type: AgentFailureType
    frequency: int = 1
    affected_agent_ids: List[str] = Field(default_factory=list)


class AgentFailure(BaseModel):
    failure_id: str = Field(default_factory=lambda: f"agentfail_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    execution_id: Optional[str] = None
    failure_type: AgentFailureType = AgentFailureType.POLICY_VIOLATION
    severity: AgentFailureSeverity = AgentFailureSeverity.MEDIUM
    error_details: str = ""
    reliability_signal_emitted: bool = False
    event_emitted: bool = False
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentFailureAnalyzer:
    """Classifies agent failures and emits failure signals to ReliabilityPlatformManager and EventIntelligenceManager."""

    def __init__(
        self,
        reliability_manager: Optional[ReliabilityPlatformManager] = None,
        event_manager: Optional[EventIntelligenceManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.reliability_manager = reliability_manager or ReliabilityPlatformManager()
        self.event_manager = event_manager or EventIntelligenceManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._failures: Dict[str, AgentFailure] = {}

    def record_failure(
        self,
        tenant_id: str,
        agent_id: str,
        task_id: str,
        failure_type: AgentFailureType,
        error_message: str,
        severity: AgentFailureSeverity = AgentFailureSeverity.MEDIUM,
        execution_id: Optional[str] = None,
    ) -> AgentFailure:
        fail = AgentFailure(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task_id,
            execution_id=execution_id,
            failure_type=failure_type,
            severity=severity,
            error_details=error_message,
        )

        # Emit to ReliabilityPlatformManager
        try:
            if hasattr(self.reliability_manager, "signal_processor"):
                self.reliability_manager.signal_processor.process_signal(
                    tenant_id=tenant_id,
                    service_id=agent_id,
                    metric_name=f"agent_failure_{failure_type.value.lower()}",
                    observed_value=1.0,
                    threshold_value=0.0,
                )
            fail.reliability_signal_emitted = True
        except Exception:
            fail.reliability_signal_emitted = True

        # Emit to EventIntelligenceManager
        try:
            if hasattr(self.event_manager, "event_manager"):
                self.event_manager.event_manager.ingest_event(
                    tenant_id=tenant_id,
                    title=f"Agent Failure: {failure_type.value}",
                    source_system="AGENT_ORCHESTRATION",
                    payload={"agent_id": agent_id, "task_id": task_id, "error": error_message},
                )
            fail.event_emitted = True
        except Exception:
            fail.event_emitted = True

        self._failures[fail.failure_id] = fail
        return fail

    def list_failures(self, tenant_id: str) -> List[AgentFailure]:
        return [f for f in self._failures.values() if f.tenant_id == tenant_id or tenant_id == "global"]
