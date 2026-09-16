"""
Workflow Steps Domain Subsystem.
Defines atomic workflow step definitions, step dependencies, types, and statuses.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowStepType(str, Enum):
    SIGNAL_ANALYSIS = "SIGNAL_ANALYSIS"
    POLICY_CHECK = "POLICY_CHECK"
    RISK_EVALUATION = "RISK_EVALUATION"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    DELEGATION_DISPATCH = "DELEGATION_DISPATCH"
    VERIFICATION_CHECK = "VERIFICATION_CHECK"
    RECOVERY_TRIGGER = "RECOVERY_TRIGGER"
    COMPENSATION_ACTION = "COMPENSATION_ACTION"
    EVIDENCE_RECORDING = "EVIDENCE_RECORDING"


class StepActionType(str, Enum):
    ANALYZE = "ANALYZE"
    RESTART_SERVICE = "RESTART_SERVICE"
    EVALUATE_POLICY = "EVALUATE_POLICY"
    DISABLE_IDENTITY = "DISABLE_IDENTITY"
    DELETE_PRODUCTION_DATA = "DELETE_PRODUCTION_DATA"
    DELEGATE_ACTION = "DELEGATE_ACTION"


class WorkflowStepStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    BLOCKED = "BLOCKED"
    RUNNING = "RUNNING"
    DELEGATED = "DELEGATED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    COMPENSATING = "COMPENSATING"


class WorkflowStepDependency(BaseModel):
    required_step_id: str
    dependency_type: str = "COMPLETION"  # COMPLETION, SUCCESS, CONDITIONAL


class WorkflowStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    step_name: str
    step_type: WorkflowStepType = WorkflowStepType.DELEGATION_DISPATCH
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    target_system: str = "OPERATIONS"
    action_name: str = "DELEGATE_ACTION"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[WorkflowStepDependency] = Field(default_factory=list)
    delegation_request_id: Optional[str] = None
    verification_result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
