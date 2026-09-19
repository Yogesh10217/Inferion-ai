"""Workflow Compensation Intelligence & Escalation (Phase 5.40)."""

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


class CompensationStatus(str, Enum):
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    UNSUPPORTED_ESCALATED = "UNSUPPORTED_ESCALATED"


class CompensationStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"comp_step_{uuid.uuid4().hex[:8]}")
    original_step_id: str
    compensation_action: str
    is_supported: bool = True
    reason_unsupported: Optional[str] = None


class CompensationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"comp_plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    execution_id: str
    status: CompensationStatus = CompensationStatus.PLANNED
    steps: List[CompensationStep] = Field(default_factory=list)
    has_unsupported_steps: bool = False
    requires_approval: bool = False
    approval_id: Optional[str] = None
    delegation_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompensationManager:
    """Manages workflow compensation planning and escalation for unsupported steps."""

    def __init__(self) -> None:
        self._plans: Dict[str, CompensationPlan] = {}

    def create_compensation_plan(
        self,
        tenant_id: str,
        execution_id: str,
        steps: List[CompensationStep],
        requires_approval: bool = False,
    ) -> CompensationPlan:
        has_unsupported = any(not s.is_supported for s in steps)
        status = CompensationStatus.UNSUPPORTED_ESCALATED if has_unsupported else CompensationStatus.PLANNED

        plan = CompensationPlan(
            tenant_id=tenant_id,
            execution_id=execution_id,
            status=status,
            steps=steps,
            has_unsupported_steps=has_unsupported,
            requires_approval=requires_approval or has_unsupported,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def approve_compensation(
        self, tenant_id: str, plan_id: str, approval_id: str = "appr_comp_123"
    ) -> CompensationPlan:
        plan = self.get_plan(tenant_id, plan_id)
        plan.approval_id = approval_id
        plan.status = CompensationStatus.APPROVED
        return plan

    def delegate_compensation(self, tenant_id: str, plan_id: str) -> DelegationRequest:
        plan = self.get_plan(tenant_id, plan_id)
        if plan.has_unsupported_steps and not plan.approval_id:
            raise HighRiskIntegrationRequiresApprovalException("COMPENSATE_UNSUPPORTED_ACTION", 90.0)

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.ORCHESTRATION,
            action="EXECUTE_WORKFLOW_COMPENSATION",
            status=DelegationStatus.QUEUED,
            payload={"plan_id": plan.plan_id, "execution_id": plan.execution_id},
        )
        plan.status = CompensationStatus.DELEGATED
        plan.delegation_request_id = del_req.delegation_id
        return del_req

    def get_plan(self, tenant_id: str, plan_id: str) -> CompensationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return plan
