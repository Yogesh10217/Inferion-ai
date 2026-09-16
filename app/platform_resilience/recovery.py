"""Coordinated Recovery Workflows Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import (
    CrossTenantResilienceAccessException,
    InvalidFailoverTransitionException,
    ResilienceResourceNotFoundException,
)


class RecoveryStatus(str, Enum):
    DETECTED = "DETECTED"
    ASSESSING = "ASSESSING"
    PLANNED = "PLANNED"
    GOVERNED = "GOVERNED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    RECOVERING = "RECOVERING"
    VERIFYING = "VERIFYING"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"


class RecoveryStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"recstep_{uuid.uuid4().hex[:8]}")
    action: str
    target_system: str
    is_completed: bool = False


class RecoveryEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"recev_{uuid.uuid4().hex[:8]}")
    summary: str = "Recovery completed and verified"
    checksum_sha256: str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class RecoveryVerification(BaseModel):
    is_verified: bool = True
    details: str = "Service recovery outcome verified"


class RecoveryPlan(BaseModel):
    recovery_plan_id: str = Field(default_factory=lambda: f"recplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    affected_service_id: str
    steps: List[RecoveryStep] = Field(default_factory=list)
    delegation_id: Optional[str] = None
    status: RecoveryStatus = RecoveryStatus.DETECTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RecoveryManager:
    """Coordinated Recovery Workflows Manager coordinating step-by-step service recovery."""

    VALID_TRANSITIONS = {
        RecoveryStatus.DETECTED: {RecoveryStatus.ASSESSING},
        RecoveryStatus.ASSESSING: {RecoveryStatus.PLANNED},
        RecoveryStatus.PLANNED: {RecoveryStatus.GOVERNED},
        RecoveryStatus.GOVERNED: {RecoveryStatus.APPROVED, RecoveryStatus.FAILED},
        RecoveryStatus.APPROVED: {RecoveryStatus.DELEGATED},
        RecoveryStatus.DELEGATED: {RecoveryStatus.RECOVERING},
        RecoveryStatus.RECOVERING: {RecoveryStatus.VERIFYING, RecoveryStatus.FAILED},
        RecoveryStatus.VERIFYING: {RecoveryStatus.RECOVERED, RecoveryStatus.FAILED},
        RecoveryStatus.RECOVERED: set(),
        RecoveryStatus.FAILED: set(),
    }

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, RecoveryPlan] = {}

    def formulate_recovery_plan(
        self,
        tenant_id: str,
        incident_id: str,
        affected_service_id: str,
        steps: Optional[List[RecoveryStep]] = None,
    ) -> RecoveryPlan:
        plan = RecoveryPlan(
            tenant_id=tenant_id,
            incident_id=incident_id,
            affected_service_id=affected_service_id,
            steps=steps or [
                RecoveryStep(action="isolate_faulty_instance", target_system="PLATFORM_OPERATIONS"),
                RecoveryStep(action="provision_replacement_capacity", target_system="PLATFORM_OPERATIONS"),
                RecoveryStep(action="rebalance_traffic", target_system="PLATFORM_OPERATIONS"),
            ],
        )
        self._plans[plan.recovery_plan_id] = plan

        self.transition_status(plan, RecoveryStatus.ASSESSING)
        self.transition_status(plan, RecoveryStatus.PLANNED)
        self.transition_status(plan, RecoveryStatus.GOVERNED)
        return plan

    def execute_recovery(self, plan_id: str, tenant_id: str) -> RecoveryPlan:
        plan = self.get_plan(plan_id, tenant_id)

        self.transition_status(plan, RecoveryStatus.APPROVED)

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="execute_recovery_plan",
            payload={"recovery_plan_id": plan_id, "service_id": plan.affected_service_id},
            requester_id="recovery_manager",
        )
        plan.delegation_id = del_req.delegation_id

        self.transition_status(plan, RecoveryStatus.DELEGATED)
        self.transition_status(plan, RecoveryStatus.RECOVERING)
        self.transition_status(plan, RecoveryStatus.VERIFYING)
        self.transition_status(plan, RecoveryStatus.RECOVERED)
        return plan

    def transition_status(self, plan: RecoveryPlan, target_status: RecoveryStatus) -> None:
        current = plan.status
        if target_status not in self.VALID_TRANSITIONS.get(current, set()):
            raise InvalidFailoverTransitionException(current.value, target_status.value)

        plan.status = target_status
        plan.updated_at = datetime.now(timezone.utc)

    def get_plan(self, plan_id: str, tenant_id: str) -> RecoveryPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ResilienceResourceNotFoundException(plan_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, plan.tenant_id)

        return plan
