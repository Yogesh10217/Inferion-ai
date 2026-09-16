"""Graceful Degradation Planning Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException, ResilienceResourceNotFoundException


class DegradationLevel(str, Enum):
    FULL = "FULL"
    REDUCED = "REDUCED"
    LIMITED = "LIMITED"
    READ_ONLY = "READ_ONLY"
    EMERGENCY = "EMERGENCY"


class DegradationStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    RESTORED = "RESTORED"


class DegradationCapability(BaseModel):
    capability_name: str
    status: str = "PRESERVED"  # PRESERVED, REDUCED, DISABLED


class DegradationPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"degpoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    allowed_levels: List[DegradationLevel] = Field(default_factory=lambda: list(DegradationLevel))


class DegradationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"degplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    level: DegradationLevel = DegradationLevel.REDUCED
    preserved_capabilities: List[str] = Field(default_factory=list)
    reduced_capabilities: List[str] = Field(default_factory=list)
    disabled_capabilities: List[str] = Field(default_factory=list)
    expected_user_impact: str = "Minimal impact; secondary features disabled."
    status: DegradationStatus = DegradationStatus.PLANNED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GracefulDegradationManager:
    """Graceful Degradation Planning Manager.

    Formulates degradation plans explicitly documenting functionality preserved, reduced, or disabled.
    """

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, DegradationPlan] = {}

    def formulate_degradation_plan(
        self,
        tenant_id: str,
        service_id: str,
        target_level: DegradationLevel = DegradationLevel.REDUCED,
        preserved: Optional[List[str]] = None,
        reduced: Optional[List[str]] = None,
        disabled: Optional[List[str]] = None,
        expected_user_impact: str = "Secondary capabilities suspended to preserve core functions.",
    ) -> DegradationPlan:
        plan = DegradationPlan(
            tenant_id=tenant_id,
            service_id=service_id,
            level=target_level,
            preserved_capabilities=preserved or ["Core Data Access", "Authentication"],
            reduced_capabilities=reduced or ["Analytics Refresh Rate"],
            disabled_capabilities=disabled or ["Background Machine Learning Pre-computation"],
            expected_user_impact=expected_user_impact,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> DegradationPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ResilienceResourceNotFoundException(plan_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, plan.tenant_id)

        return plan
