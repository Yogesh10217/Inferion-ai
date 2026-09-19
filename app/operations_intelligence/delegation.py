"""Delegated Operational Action Coordination (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    HighRiskOperationRequiresApprovalException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationStatus, DelegationTarget


class OperationalDelegationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"del_plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action_type: str
    target_service_id: str
    requires_approval: bool = False
    approval_id: Optional[str] = None
    delegation_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalDelegationManager:
    """Coordinates external operational actions strictly through DelegationRequest."""

    def __init__(self) -> None:
        self._plans: Dict[str, OperationalDelegationPlan] = {}

    def create_delegation_plan(
        self,
        tenant_id: str,
        action_type: str,
        target_service_id: str,
        requires_approval: bool = False,
    ) -> OperationalDelegationPlan:
        plan = OperationalDelegationPlan(
            tenant_id=tenant_id,
            action_type=action_type,
            target_service_id=target_service_id,
            requires_approval=requires_approval,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def approve_plan(
        self, tenant_id: str, plan_id: str, approval_id: str = "appr_del_999"
    ) -> OperationalDelegationPlan:
        plan = self.get_plan(tenant_id, plan_id)
        plan.approval_id = approval_id
        return plan

    def execute_delegation(self, tenant_id: str, plan_id: str) -> DelegationRequest:
        plan = self.get_plan(tenant_id, plan_id)
        if plan.requires_approval and not plan.approval_id:
            raise HighRiskOperationRequiresApprovalException(plan.action_type, 85.0)

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action=plan.action_type,
            status=DelegationStatus.QUEUED,
            payload={"plan_id": plan.plan_id, "target_service_id": plan.target_service_id},
        )
        plan.delegation_request_id = del_req.delegation_id
        return del_req

    def get_plan(self, tenant_id: str, plan_id: str) -> OperationalDelegationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return plan
