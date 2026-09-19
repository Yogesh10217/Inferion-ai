"""Controlled Failover Orchestration Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import (
    CrossTenantResilienceAccessException,
    HighRiskRecoveryRequiresApprovalException,
    InvalidFailoverTransitionException,
    ResilienceResourceNotFoundException,
)


class FailoverStatus(str, Enum):
    REQUESTED = "REQUESTED"
    ASSESSING = "ASSESSING"
    GOVERNED = "GOVERNED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class FailoverTarget(BaseModel):
    target_id: str
    target_region: str
    target_cluster: str = "primary-replica"


class FailoverDecision(BaseModel):
    is_approved: bool = False
    requires_human_approval: bool = True
    governance_reason: str = "High-risk regional failover requires approval."


class FailoverVerification(BaseModel):
    is_verified: bool = False
    verification_details: str = "Pending failover execution"


class FailoverPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"failplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    source_region: str
    target_region: str
    affected_resource_scope: List[str] = Field(default_factory=list)
    maximum_impact_boundary: str = "SINGLE_TENANT_SERVICE"
    rollback_reference_id: Optional[str] = None
    delegation_id: Optional[str] = None
    status: FailoverStatus = FailoverStatus.REQUESTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FailoverRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"failreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    source_region: str = "us-east-1"
    target_region: str = "us-west-2"
    reason: str = "Region outage or severe degradation"
    is_high_risk: bool = True


class FailoverManager:
    """Controlled Failover Orchestration Manager supporting explicit state machine transitions and blast-radius controls."""

    VALID_TRANSITIONS = {
        FailoverStatus.REQUESTED: {FailoverStatus.ASSESSING},
        FailoverStatus.ASSESSING: {FailoverStatus.GOVERNED},
        FailoverStatus.GOVERNED: {FailoverStatus.APPROVED, FailoverStatus.FAILED},
        FailoverStatus.APPROVED: {FailoverStatus.DELEGATED},
        FailoverStatus.DELEGATED: {FailoverStatus.EXECUTING},
        FailoverStatus.EXECUTING: {FailoverStatus.VERIFYING, FailoverStatus.FAILED},
        FailoverStatus.VERIFYING: {FailoverStatus.COMPLETED, FailoverStatus.FAILED, FailoverStatus.ROLLED_BACK},
        FailoverStatus.COMPLETED: set(),
        FailoverStatus.FAILED: {FailoverStatus.ROLLED_BACK},
        FailoverStatus.ROLLED_BACK: set(),
    }

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, FailoverPlan] = {}

    def create_failover_request(
        self,
        tenant_id: str,
        service_id: str,
        source_region: str = "us-east-1",
        target_region: str = "us-west-2",
        reason: str = "Region outage",
        is_high_risk: bool = True,
    ) -> FailoverPlan:
        plan = FailoverPlan(
            tenant_id=tenant_id,
            service_id=service_id,
            source_region=source_region,
            target_region=target_region,
            affected_resource_scope=[service_id, f"db_{service_id}"],
            maximum_impact_boundary=f"TENANT_{tenant_id}_REGION_{source_region}",
            rollback_reference_id=f"rollback_{uuid.uuid4().hex[:8]}",
        )
        self._plans[plan.plan_id] = plan

        # State machine transition: REQUESTED -> ASSESSING -> GOVERNED
        self.transition_status(plan, FailoverStatus.ASSESSING)
        self.transition_status(plan, FailoverStatus.GOVERNED)

        if is_high_risk:
            # High-risk failover requires approval
            raise HighRiskRecoveryRequiresApprovalException(
                f"Failover request '{plan.plan_id}' for service '{service_id}' from '{source_region}' to '{target_region}' requires human approval."
            )

        return plan

    def approve_and_delegate_failover(self, plan_id: str, tenant_id: str) -> FailoverPlan:
        plan = self.get_plan(plan_id, tenant_id)

        self.transition_status(plan, FailoverStatus.APPROVED)

        # Create DelegationRequest
        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="execute_regional_failover",
            payload={
                "service_id": plan.service_id,
                "source_region": plan.source_region,
                "target_region": plan.target_region,
            },
            requester_id="failover_manager",
        )
        plan.delegation_id = del_req.delegation_id

        self.transition_status(plan, FailoverStatus.DELEGATED)
        self.transition_status(plan, FailoverStatus.EXECUTING)
        self.transition_status(plan, FailoverStatus.VERIFYING)
        self.transition_status(plan, FailoverStatus.COMPLETED)

        return plan

    def transition_status(self, plan: FailoverPlan, target_status: FailoverStatus) -> None:
        current = plan.status
        if target_status not in self.VALID_TRANSITIONS.get(current, set()):
            raise InvalidFailoverTransitionException(current.value, target_status.value)

        plan.status = target_status
        plan.updated_at = datetime.now(timezone.utc)

    def get_plan(self, plan_id: str, tenant_id: str) -> FailoverPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ResilienceResourceNotFoundException(plan_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, plan.tenant_id)

        return plan
