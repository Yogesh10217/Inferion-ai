"""Controlled Integration Recovery (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    HighRiskIntegrationRequiresApprovalException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationStatus, DelegationTarget


class RecoveryStatus(str, Enum):
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class RecoveryStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"rec_step_{uuid.uuid4().hex[:8]}")
    action: str  # e.g., "REROUTE_TRAFFIC", "RETRY_DEFERRED_MESSAGES", "TRIGGER_HEALTH_CHECK"
    target_system_id: str
    is_high_risk: bool = False


class IntegrationRecoveryPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rec_plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    failure_id: str
    status: RecoveryStatus = RecoveryStatus.PLANNED
    steps: List[RecoveryStep] = Field(default_factory=list)
    requires_approval: bool = False
    approval_id: Optional[str] = None
    delegation_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationRecoveryManager:
    """Manages integration recovery plans and delegated recovery execution."""

    def __init__(self) -> None:
        self._plans: Dict[str, IntegrationRecoveryPlan] = {}

    def create_recovery_plan(
        self,
        tenant_id: str,
        failure_id: str,
        steps: List[RecoveryStep],
        requires_approval: bool = False,
    ) -> IntegrationRecoveryPlan:
        plan = IntegrationRecoveryPlan(
            tenant_id=tenant_id,
            failure_id=failure_id,
            steps=steps,
            requires_approval=requires_approval,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def approve_recovery(
        self, tenant_id: str, plan_id: str, approval_id: str = "appr_rec_123"
    ) -> IntegrationRecoveryPlan:
        plan = self.get_plan(tenant_id, plan_id)
        plan.approval_id = approval_id
        plan.status = RecoveryStatus.APPROVED
        return plan

    def delegate_recovery(self, tenant_id: str, plan_id: str) -> DelegationRequest:
        plan = self.get_plan(tenant_id, plan_id)
        if plan.requires_approval and not plan.approval_id:
            raise HighRiskIntegrationRequiresApprovalException("EXECUTE_RECOVERY_PLAN", 80.0)

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="EXECUTE_INTEGRATION_RECOVERY",
            status=DelegationStatus.QUEUED,
            payload={"plan_id": plan.plan_id, "failure_id": plan.failure_id},
        )
        plan.status = RecoveryStatus.DELEGATED
        plan.delegation_request_id = del_req.delegation_id
        return del_req

    def get_plan(self, tenant_id: str, plan_id: str) -> IntegrationRecoveryPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return plan
