"""Access Remediation Planning & Delegation-Only Execution (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import (
    CrossTenantAccessIntelligenceException,
    AccessDelegationBlockedException,
    HighRiskAccessRequiresApprovalException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget, DelegationStatus


class AccessRemediationAction(str, Enum):
    REVOKE_ENTITLEMENT = "REVOKE_ENTITLEMENT"
    REDUCE_SCOPE = "REDUCE_SCOPE"
    EXPIRE_ACCESS = "EXPIRE_ACCESS"
    REQUIRE_RECERTIFICATION = "REQUIRE_RECERTIFICATION"
    DISABLE_STALE_ACCESS = "DISABLE_STALE_ACCESS"


class AccessRemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    IMMEDIATE = "IMMEDIATE"


class AccessRemediationStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class AccessRemediationPlan(BaseModel):
    """Access Remediation Plan."""
    plan_id: str = Field(default_factory=lambda: f"rem_plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_identity_id: str
    action: AccessRemediationAction
    target_entitlement_id: str
    priority: AccessRemediationPriority = AccessRemediationPriority.HIGH
    status: AccessRemediationStatus = AccessRemediationStatus.PLANNED
    requires_approval: bool = False
    approval_id: Optional[str] = None
    delegation_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessRemediationManager:
    """Manages remediation plans and delegated execution requests."""

    def __init__(self) -> None:
        self._plans: Dict[str, AccessRemediationPlan] = {}

    def create_remediation_plan(
        self,
        tenant_id: str,
        target_identity_id: str,
        action: AccessRemediationAction,
        target_entitlement_id: str,
        priority: AccessRemediationPriority = AccessRemediationPriority.HIGH,
        requires_approval: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessRemediationPlan:
        plan = AccessRemediationPlan(
            tenant_id=tenant_id,
            target_identity_id=target_identity_id,
            action=action,
            target_entitlement_id=target_entitlement_id,
            priority=priority,
            requires_approval=requires_approval,
            metadata=metadata or {},
        )
        self._plans[plan.plan_id] = plan
        return plan

    def delegate_remediation(self, tenant_id: str, plan_id: str) -> DelegationRequest:
        plan = self.get_plan(tenant_id, plan_id)
        if plan.requires_approval and not plan.approval_id:
            raise HighRiskAccessRequiresApprovalException(plan.plan_id, 85.0)

        delegation_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action=f"ACCESS_REMEDIATION_{plan.action.value}",
            status=DelegationStatus.QUEUED,
            payload={
                "plan_id": plan.plan_id,
                "target_identity_id": plan.target_identity_id,
                "target_entitlement_id": plan.target_entitlement_id,
                "action": plan.action.value,
            },
        )

        plan.status = AccessRemediationStatus.DELEGATED
        plan.delegation_request_id = delegation_req.delegation_id
        return delegation_req

    def approve_remediation(self, tenant_id: str, plan_id: str, approval_id: str = "appr_rem_123") -> AccessRemediationPlan:
        plan = self.get_plan(tenant_id, plan_id)
        plan.approval_id = approval_id
        return plan

    def get_plan(self, tenant_id: str, plan_id: str) -> AccessRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return plan

    def list_plans(self, tenant_id: str, status: Optional[AccessRemediationStatus] = None) -> List[AccessRemediationPlan]:
        results = [p for p in self._plans.values() if p.tenant_id == tenant_id]
        if status:
            results = [p for p in results if p.status == status]
        return results
