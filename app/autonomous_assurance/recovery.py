"""
Recovery Planning Subsystem.
Constructs recovery plans when workflow steps or delegated actions fail.
Does NOT directly mutate external infrastructure.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class RecoveryStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"recstep_{uuid.uuid4().hex[:12]}")
    action_type: str = "DELEGATE_RECOVERY"
    target_system: str = "OPERATIONS"
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RecoveryPlan(BaseModel):
    recovery_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    failure_reason: str
    recovery_strategy: str = "FALLBACK_RETRY"
    failed_step_id: Optional[str] = None
    recovery_steps: List[RecoveryStep] = Field(default_factory=list)
    status: str = "PLANNED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RecoveryPlanner:
    """Constructs delegated recovery plans upon workflow failures."""

    def __init__(self) -> None:
        self._plans: Dict[str, RecoveryPlan] = {}

    def plan_recovery(
        self,
        workflow_id: str,
        tenant_id: str,
        failure_reason: str = "Step verification failure",
        failed_step_id: Optional[str] = None,
        trigger_reason: Optional[str] = None,
    ) -> RecoveryPlan:
        reason = trigger_reason or failure_reason
        steps = [
            RecoveryStep(action_type="DELEGATE_ROLLBACK", target_system="OPERATIONS", parameters={"mode": "SAFE"}),
            RecoveryStep(action_type="VERIFY_RECOVERY_HEALTH", target_system="OPERATIONS_ASSURANCE"),
        ]
        plan = RecoveryPlan(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            failure_reason=reason,
            failed_step_id=failed_step_id,
            recovery_steps=steps,
        )
        self._plans[workflow_id] = plan
        return plan

    def get_recovery_plan(self, workflow_id: str) -> Optional[RecoveryPlan]:
        return self._plans.get(workflow_id)
