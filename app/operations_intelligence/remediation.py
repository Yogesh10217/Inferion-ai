"""Operational Remediation Planning & Delegation-Only Execution (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    HighRiskOperationRequiresApprovalException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationStatus, DelegationTarget
from app.platform_contracts.idempotency import IdempotencyManager, IdempotencyStatus


class RemediationPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class RemediationStatus(str, Enum):
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class RemediationAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"rem_act_{uuid.uuid4().hex[:8]}")
    action_name: str  # RESTART_SERVICE, FAILOVER_DB, ROLLBACK_DEPLOYMENT, SCALE_UP
    target_service_id: str
    is_high_risk: bool = False


class OperationalRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rem_plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    idempotency_key: str
    status: RemediationStatus = RemediationStatus.PLANNED
    priority: RemediationPriority = RemediationPriority.P2
    actions: List[RemediationAction] = Field(default_factory=list)
    requires_approval: bool = False
    approval_id: Optional[str] = None
    delegation_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalRemediationManager:
    """Manages operational remediation planning via DelegationRequest (no direct production mutation)."""

    def __init__(self) -> None:
        self._plans: Dict[str, OperationalRemediationPlan] = {}
        self.idempotency_manager = IdempotencyManager()

    def create_remediation_plan(
        self,
        tenant_id: str,
        incident_id: str,
        idempotency_key: str,
        actions: List[RemediationAction],
        priority: RemediationPriority = RemediationPriority.P2,
        requires_approval: bool = False,
    ) -> OperationalRemediationPlan:
        # Idempotency check
        existing_record = self.idempotency_manager.check_or_start(
            tenant_id=tenant_id,
            operation_type="OPERATIONAL_REMEDIATION",
            idempotency_key=idempotency_key,
            request_payload={"incident_id": incident_id},
        )
        if existing_record and existing_record.result_payload:
            existing_plan_id = existing_record.result_payload.get("plan_id")
            if existing_plan_id and existing_plan_id in self._plans:
                return self._plans[existing_plan_id]

        has_high_risk = any(a.is_high_risk for a in actions)
        plan = OperationalRemediationPlan(
            tenant_id=tenant_id,
            incident_id=incident_id,
            idempotency_key=idempotency_key,
            actions=actions,
            priority=priority,
            requires_approval=requires_approval or has_high_risk,
        )
        self._plans[plan.plan_id] = plan

        self.idempotency_manager.complete_operation(
            tenant_id=tenant_id,
            operation_type="OPERATIONAL_REMEDIATION",
            idempotency_key=idempotency_key,
            result_payload={"plan_id": plan.plan_id},
            status=IdempotencyStatus.RUNNING,
        )
        return plan

    def approve_remediation(
        self, tenant_id: str, plan_id: str, approval_id: str = "appr_rem_123"
    ) -> OperationalRemediationPlan:
        plan = self.get_plan(tenant_id, plan_id)
        plan.approval_id = approval_id
        plan.status = RemediationStatus.APPROVED
        return plan

    def delegate_remediation(self, tenant_id: str, plan_id: str) -> DelegationRequest:
        plan = self.get_plan(tenant_id, plan_id)
        if plan.requires_approval and not plan.approval_id:
            raise HighRiskOperationRequiresApprovalException("EXECUTE_REMEDIATION_ACTION", 85.0)

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="EXECUTE_OPERATIONAL_REMEDIATION",
            status=DelegationStatus.QUEUED,
            payload={"plan_id": plan.plan_id, "incident_id": plan.incident_id},
        )
        plan.status = RemediationStatus.DELEGATED
        plan.delegation_request_id = del_req.delegation_id
        return del_req

    def get_plan(self, tenant_id: str, plan_id: str) -> OperationalRemediationPlan:
        plan = self._plans.get(plan_id)
        if not plan or plan.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return plan
