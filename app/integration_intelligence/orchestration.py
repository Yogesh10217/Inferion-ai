"""Integration Orchestration Planning (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class IntegrationPlanStatus(str, Enum):
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IntegrationPlanStep(BaseModel):
    """Step in an integration execution plan."""
    step_id: str = Field(default_factory=lambda: f"plan_step_{uuid.uuid4().hex[:8]}")
    step_order: int
    name: str
    target_connector_id: str
    target_endpoint_id: str
    action_type: str
    is_high_risk: bool = False


class IntegrationPlan(BaseModel):
    """Governed Integration Plan Representation."""
    plan_id: str = Field(default_factory=lambda: f"plan_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    workflow_id: str
    name: str
    status: IntegrationPlanStatus = IntegrationPlanStatus.PLANNED
    steps: List[IntegrationPlanStep] = Field(default_factory=list)
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationOrchestrationManager:
    """Creates governed integration plans by reusing platform orchestration primitives."""

    def __init__(self) -> None:
        self._plans: Dict[str, IntegrationPlan] = {}

    def create_plan(
        self,
        tenant_id: str,
        workflow_id: str,
        name: str,
        steps: List[IntegrationPlanStep],
        requires_approval: bool = False,
    ) -> IntegrationPlan:
        plan = IntegrationPlan(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            name=name,
            steps=steps,
            requires_approval=requires_approval,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, tenant_id: str, plan_id: str) -> IntegrationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return plan

    def list_plans(self, tenant_id: str) -> List[IntegrationPlan]:
        return [p for p in self._plans.values() if p.tenant_id == tenant_id]
