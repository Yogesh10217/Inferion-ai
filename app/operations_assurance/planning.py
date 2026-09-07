"""Autonomous operational planning with strict recommendation -> governance -> approval -> delegation flow."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, OperationalPlanNotFoundException


class PlanningStrategy(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"
    EMERGENCY = "EMERGENCY"


class OperationalPlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order: int
    title: str
    action_type: str
    requires_approval: bool = True
    delegation_target: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)


class OperationalPlanStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class OperationalPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    strategy: PlanningStrategy = PlanningStrategy.BALANCED
    status: OperationalPlanStatus = OperationalPlanStatus.DRAFT
    steps: List[OperationalPlanStep] = Field(default_factory=list)
    auto_execute: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalPlanAssessment(BaseModel):
    plan_id: str
    tenant_id: str
    risk_level: str = "HIGH"
    governance_passed: bool = False
    requires_human_approval: bool = True
    notes: str = ""


class OperationalPlanner:
    """Generates multi-step operational plans ensuring governance and human approval before delegation."""

    def __init__(self) -> None:
        self._plans: Dict[str, Dict[str, OperationalPlan]] = {}  # tenant_id -> {plan_id: plan}

    def create_plan(
        self,
        tenant_id: str,
        service_id: str,
        strategy: PlanningStrategy = PlanningStrategy.BALANCED,
        steps: Optional[List[OperationalPlanStep]] = None,
    ) -> OperationalPlan:
        plan = OperationalPlan(
            tenant_id=tenant_id,
            service_id=service_id,
            strategy=strategy,
            steps=steps or [],
            auto_execute=False,
        )
        if tenant_id not in self._plans:
            self._plans[tenant_id] = {}
        self._plans[tenant_id][plan.plan_id] = plan
        return plan

    def assess_plan(self, tenant_id: str, plan_id: str) -> OperationalPlanAssessment:
        plan = self.get_plan(tenant_id, plan_id)
        has_high_risk = any(step.requires_approval for step in plan.steps)
        return OperationalPlanAssessment(
            plan_id=plan.plan_id,
            tenant_id=tenant_id,
            risk_level="HIGH" if has_high_risk else "MEDIUM",
            governance_passed=True,
            requires_human_approval=has_high_risk or True,
            notes="Plan must be routed through approval engine prior to delegation.",
        )

    def get_plan(self, tenant_id: str, plan_id: str) -> OperationalPlan:
        if tenant_id not in self._plans or plan_id not in self._plans[tenant_id]:
            for tid, plans in self._plans.items():
                if tid != tenant_id and plan_id in plans:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise OperationalPlanNotFoundException("Operational plan not found.")
        return self._plans[tenant_id][plan_id]
