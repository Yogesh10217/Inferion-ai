"""
Delegated Execution Tracking Subsystem.
Tracks external execution state of delegated requests.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class DelegatedExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"ex_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    delegation_request_id: str = "del_req_default"
    status: ExecutionStatus = ExecutionStatus.CREATED
    total_steps: int = 1
    completed_steps: int = 0
    progress_percentage: float = 0.0
    result: Optional[Dict[str, Any]] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionTracker:
    """Tracks status of delegated execution tasks."""

    def __init__(self) -> None:
        self._executions: Dict[str, DelegatedExecution] = {}

    def track_execution(self, workflow_id: str, tenant_id: str, delegation_request_id: str, status: ExecutionStatus = ExecutionStatus.SUBMITTED) -> DelegatedExecution:
        ex = DelegatedExecution(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            delegation_request_id=delegation_request_id,
            status=status,
        )
        self._executions[workflow_id] = ex
        return ex

    def start_tracking(self, workflow_id: str, tenant_id: str, total_steps: int = 1) -> DelegatedExecution:
        ex = DelegatedExecution(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            delegation_request_id="del_req_default",
            total_steps=total_steps,
            completed_steps=0,
            progress_percentage=0.0,
            status=ExecutionStatus.RUNNING,
        )
        self._executions[workflow_id] = ex
        return ex

    def record_step_completion(self, workflow_id: str, tenant_id: str, step_id: str) -> DelegatedExecution:
        ex = self._executions.get(workflow_id)
        if not ex:
            ex = self.start_tracking(workflow_id, tenant_id)
        ex.completed_steps += 1
        ex.progress_percentage = round((ex.completed_steps / max(ex.total_steps, 1)) * 100, 2)
        ex.updated_at = datetime.now(timezone.utc)
        return ex

    def update_status(self, workflow_id: str, status: ExecutionStatus, result: Optional[Dict[str, Any]] = None) -> Optional[DelegatedExecution]:
        ex = self._executions.get(workflow_id)
        if ex:
            ex.status = status
            ex.result = result or {}
            ex.updated_at = datetime.now(timezone.utc)
        return ex

    def get_execution(self, workflow_id: str) -> Optional[DelegatedExecution]:
        return self._executions.get(workflow_id)
