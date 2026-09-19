"""
Workflow Runtime State Tracking Subsystem (Addition #4).
Tracks distributed execution state, active execution nodes, heartbeat timers, and step progress.
Does NOT directly execute infrastructure actions.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.autonomous_assurance.exceptions import (
    CrossTenantAutonomousAssuranceException,
)


class WorkflowRuntimeState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    WAITING_DELEGATION = "WAITING_DELEGATION"
    WAITING_VERIFICATION = "WAITING_VERIFICATION"
    RECOVERING = "RECOVERING"
    COMPENSATING = "COMPENSATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkflowRuntimeRecord(BaseModel):
    runtime_id: str = Field(default_factory=lambda: f"wfrun_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    current_state: WorkflowRuntimeState = WorkflowRuntimeState.PENDING
    active_step_id: Optional[str] = None
    step_progress_pct: float = 0.0
    delegation_request_ids: List[str] = Field(default_factory=list)
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state_history: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowRuntimeEngine:
    """Manages distributed workflow runtime tracking without infrastructure execution."""

    def __init__(self) -> None:
        self._runtimes: Dict[str, WorkflowRuntimeRecord] = {}

    def init_runtime(self, workflow_id: str, tenant_id: str) -> WorkflowRuntimeRecord:
        record = WorkflowRuntimeRecord(workflow_id=workflow_id, tenant_id=tenant_id)
        self._runtimes[workflow_id] = record
        return record

    def update_runtime_state(
        self,
        workflow_id: str,
        tenant_id: str,
        target_state: WorkflowRuntimeState,
        active_step_id: Optional[str] = None,
        progress_pct: Optional[float] = None,
        reason: str = "State transition",
    ) -> WorkflowRuntimeRecord:
        record = self.get_runtime(workflow_id, tenant_id)
        record.state_history.append(
            {
                "from_state": record.current_state.value,
                "to_state": target_state.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            }
        )
        record.current_state = target_state
        if active_step_id:
            record.active_step_id = active_step_id
        if progress_pct is not None:
            record.step_progress_pct = progress_pct
        record.last_heartbeat = datetime.now(timezone.utc)
        record.updated_at = datetime.now(timezone.utc)
        return record

    def get_runtime(self, workflow_id: str, tenant_id: str) -> WorkflowRuntimeRecord:
        record = self._runtimes.get(workflow_id)
        if not record:
            record = self.init_runtime(workflow_id, tenant_id)
        if record.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantAutonomousAssuranceException(
                f"Unauthorized cross-tenant access to workflow runtime '{workflow_id}'"
            )
        return record
