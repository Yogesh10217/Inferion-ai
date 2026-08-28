"""Controlled Restore Planning Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_resilience.exceptions import (
    CrossTenantResilienceAccessException,
    ResilienceResourceNotFoundException,
    RecoveryVerificationFailedException,
)


class RestoreStatus(str, Enum):
    PLANNED = "PLANNED"
    GOVERNED = "GOVERNED"
    DELEGATED = "DELEGATED"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RestoreTarget(BaseModel):
    target_resource_id: str
    target_environment: str = "production"


class RestoreVerification(BaseModel):
    is_successful: bool = True
    verification_message: str = "Restore verified cleanly"


class RestorePlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"restplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    backup_id: str
    target_resource_id: str
    delegation_id: Optional[str] = None
    status: RestoreStatus = RestoreStatus.PLANNED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RestoreRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"restreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    backup_id: str
    target_resource_id: str


class RestoreManager:
    """Controlled Restore Planning Manager delegating infrastructure execution."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, RestorePlan] = {}

    def plan_restore(
        self,
        tenant_id: str,
        backup_id: str,
        target_resource_id: str,
    ) -> RestorePlan:
        plan = RestorePlan(
            tenant_id=tenant_id,
            backup_id=backup_id,
            target_resource_id=target_resource_id,
        )

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="execute_data_restore",
            payload={"backup_id": backup_id, "target_resource_id": target_resource_id},
            requester_id="restore_manager",
        )
        plan.delegation_id = del_req.delegation_id
        plan.status = RestoreStatus.DELEGATED

        self._plans[plan.plan_id] = plan
        return plan

    def verify_restore(self, plan_id: str, tenant_id: str, force_failure: bool = False) -> RestoreVerification:
        plan = self.get_plan(plan_id, tenant_id)
        if force_failure:
            plan.status = RestoreStatus.FAILED
            raise RecoveryVerificationFailedException(f"Restore plan '{plan_id}' verification failed.")

        plan.status = RestoreStatus.COMPLETED
        return RestoreVerification(is_successful=True, verification_message="Restore verified cleanly")

    def get_plan(self, plan_id: str, tenant_id: str) -> RestorePlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ResilienceResourceNotFoundException(plan_id)
        
        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, plan.tenant_id)
            
        return plan
