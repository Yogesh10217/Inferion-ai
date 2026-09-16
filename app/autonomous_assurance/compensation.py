"""
Compensation Planning Subsystem.
Constructs compensation steps to reverse or mitigate partial workflow execution effects.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CompensationStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"compstep_{uuid.uuid4().hex[:12]}")
    original_step_id: str
    action_type: str = "DELEGATE_COMPENSATION"
    target_system: str = "OPERATIONS"
    parameters: Dict[str, Any] = Field(default_factory=dict)


class CompensationPlan(BaseModel):
    compensation_id: str = Field(default_factory=lambda: f"comp_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    failed_step_id: str = "step_001"
    completed_steps: List[str] = Field(default_factory=list)
    compensation_steps: List[CompensationStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompensationPlanner:
    """Constructs step compensation plans."""

    def __init__(self) -> None:
        self._plans: Dict[str, CompensationPlan] = {}

    def plan_compensation(
        self,
        workflow_id: str,
        tenant_id: str,
        failed_step_id: str = "step_001",
        completed_steps: Optional[List[str]] = None,
    ) -> CompensationPlan:
        steps_to_compensate = completed_steps or [failed_step_id]
        steps = [
            CompensationStep(
                original_step_id=sid,
                action_type="DELEGATE_RESTORE_CONFIG",
                target_system="OPERATIONS",
            )
            for sid in steps_to_compensate
        ]
        plan = CompensationPlan(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            failed_step_id=failed_step_id,
            completed_steps=steps_to_compensate,
            compensation_steps=steps,
        )
        self._plans[workflow_id] = plan
        return plan

    def get_compensation_plan(self, workflow_id: str) -> Optional[CompensationPlan]:
        return self._plans.get(workflow_id)
