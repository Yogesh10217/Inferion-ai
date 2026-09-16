"""Autonomous planning intelligence for multi-step decision execution plans."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    DecisionPlanningException,
    DecisionPlanNotFoundException,
)


class PlanStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ANALYZING = "ANALYZING"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PlanPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PlanRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PlanningStrategy(str, Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    CONDITIONAL = "CONDITIONAL"
    ADAPTIVE = "ADAPTIVE"


class DecisionPlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sequence_order: int
    name: str
    action_type: str
    target_domain: str
    description: str = ""
    dependencies: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: PlanRisk = PlanRisk.LOW
    requires_approval: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    name: str
    description: str = ""
    status: PlanStatus = PlanStatus.PROPOSED
    priority: PlanPriority = PlanPriority.MEDIUM
    overall_risk: PlanRisk = PlanRisk.MEDIUM
    strategy: PlanningStrategy = PlanningStrategy.SEQUENTIAL
    steps: List[DecisionPlanStep] = Field(default_factory=list)
    feasibility_score: float = 1.0
    estimated_duration_seconds: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionPlanningManager:
    """Manages multi-step autonomous decision plans. Plans are advisory & delegation-only."""

    def __init__(self) -> None:
        self._plans: Dict[str, DecisionPlan] = {}

    def create_plan(
        self,
        tenant_id: str,
        decision_id: str,
        name: str,
        steps: List[DecisionPlanStep],
        description: str = "",
        strategy: PlanningStrategy = PlanningStrategy.SEQUENTIAL,
        priority: PlanPriority = PlanPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionPlan:
        if not steps:
            raise DecisionPlanningException("Decision plan must contain at least one step")

        # Evaluate risk and feasibility
        max_risk = PlanRisk.LOW
        risk_map = {PlanRisk.LOW: 1, PlanRisk.MEDIUM: 2, PlanRisk.HIGH: 3, PlanRisk.CRITICAL: 4}
        for s in steps:
            if risk_map[s.risk_level] > risk_map[max_risk]:
                max_risk = s.risk_level

        plan = DecisionPlan(
            tenant_id=tenant_id,
            decision_id=decision_id,
            name=name,
            description=description,
            strategy=strategy,
            priority=priority,
            overall_risk=max_risk,
            steps=sorted(steps, key=lambda x: x.sequence_order),
            feasibility_score=0.95 if max_risk != PlanRisk.CRITICAL else 0.70,
            metadata=metadata or {},
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> DecisionPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise DecisionPlanNotFoundException(f"Plan '{plan_id}' not found")
        if plan.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return plan

    def list_plans_for_decision(self, decision_id: str, tenant_id: str) -> List[DecisionPlan]:
        return [p for p in self._plans.values() if p.decision_id == decision_id and p.tenant_id == tenant_id]

    def update_plan_status(self, plan_id: str, tenant_id: str, status: PlanStatus) -> DecisionPlan:
        plan = self.get_plan(plan_id, tenant_id)
        plan.status = status
        plan.updated_at = datetime.now(timezone.utc)
        return plan
