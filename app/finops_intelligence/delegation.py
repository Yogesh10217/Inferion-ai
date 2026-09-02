"""Delegated Financial Action Coordination (Phase 5.42)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import (
    CrossTenantFinOpsIntelligenceException,
    HighRiskOptimizationRequiresApprovalException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget, DelegationStatus


class FinOpsDelegationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_fin_{uuid.uuid4().hex[:8]}")
    action_type: str  # DOWNSIZE_RESOURCE, RIGHTSIZE_MODEL, TERMINATE_IDLE_WORKLOAD, ADJUST_BUDGET
    target_resource_id: str
    is_high_risk: bool = False


class FinOpsDelegationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"del_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    optimization_id: str
    actions: List[FinOpsDelegationAction] = Field(default_factory=list)
    requires_approval: bool = False
    approval_id: Optional[str] = None
    delegation_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsDelegationManager:
    """Coordinates financial execution actions strictly through DelegationRequest."""

    def __init__(self) -> None:
        self._plans: Dict[str, FinOpsDelegationPlan] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        optimization_id: str,
        actions: List[FinOpsDelegationAction],
        requires_approval: bool = False,
    ) -> FinOpsDelegationPlan:
        has_high_risk = any(a.is_high_risk for a in actions)
        plan = FinOpsDelegationPlan(
            tenant_id=tenant_id,
            optimization_id=optimization_id,
            actions=actions,
            requires_approval=requires_approval or has_high_risk,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def approve_plan(self, tenant_id: str, plan_id: str, approval_id: str = "appr_fin_del_123") -> FinOpsDelegationPlan:
        plan = self.get_plan(tenant_id, plan_id)
        plan.approval_id = approval_id
        return plan

    def execute_delegation(self, tenant_id: str, plan_id: str) -> DelegationRequest:
        plan = self.get_plan(tenant_id, plan_id)
        if plan.requires_approval and not plan.approval_id:
            raise HighRiskOptimizationRequiresApprovalException(
                action_name=plan.actions[0].action_type if plan.actions else "FINANCIAL_OPTIMIZATION",
                estimated_savings=5000.0,
            )

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="EXECUTE_FINANCIAL_OPTIMIZATION",
            status=DelegationStatus.QUEUED,
            payload={"plan_id": plan.plan_id, "optimization_id": plan.optimization_id},
        )
        plan.delegation_request_id = del_req.delegation_id
        return del_req

    def get_plan(self, tenant_id: str, plan_id: str) -> FinOpsDelegationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return plan
