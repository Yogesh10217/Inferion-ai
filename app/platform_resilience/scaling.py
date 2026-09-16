"""Scaling Governance & Planning Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException, ResilienceResourceNotFoundException


class ScalingTrigger(str, Enum):
    CPU_UTILIZATION = "CPU_UTILIZATION"
    MEMORY_UTILIZATION = "MEMORY_UTILIZATION"
    REQUEST_RATE = "REQUEST_RATE"
    QUEUE_DEPTH = "QUEUE_DEPTH"
    MANUAL = "MANUAL"


class ScalingDirection(str, Enum):
    SCALE_OUT = "SCALE_OUT"
    SCALE_IN = "SCALE_IN"
    INCREASE_CAPACITY = "INCREASE_CAPACITY"
    REDUCE_CAPACITY = "REDUCE_CAPACITY"


class ScalingStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ScalingAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"scaleact_{uuid.uuid4().hex[:12]}")
    target_resource_id: str
    direction: ScalingDirection = ScalingDirection.SCALE_OUT
    delta_units: int = 2
    reason: str = "Capacity threshold reached"


class ScalingPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"scalepoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    min_instances: int = 2
    max_instances: int = 20
    cooldown_seconds: int = 300


class ScalingPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"scaleplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    direction: ScalingDirection = ScalingDirection.SCALE_OUT
    actions: List[ScalingAction] = Field(default_factory=list)
    delegation_id: Optional[str] = None
    status: ScalingStatus = ScalingStatus.PLANNED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScalingManager:
    """Scaling Governance and Planning Manager.

    Generates non-mutating scaling plans and delegates infrastructure mutation via DelegationRequest.
    """

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, ScalingPlan] = {}
        self._policies: Dict[str, ScalingPolicy] = {}

    def set_scaling_policy(
        self,
        tenant_id: str,
        resource_id: str,
        min_instances: int = 2,
        max_instances: int = 20,
    ) -> ScalingPolicy:
        poly = ScalingPolicy(
            tenant_id=tenant_id,
            resource_id=resource_id,
            min_instances=min_instances,
            max_instances=max_instances,
        )
        self._policies[f"{tenant_id}:{resource_id}"] = poly
        return poly

    def plan_scaling(
        self,
        tenant_id: str,
        resource_id: str,
        direction: ScalingDirection = ScalingDirection.SCALE_OUT,
        delta_units: int = 2,
        reason: str = "Capacity saturation threshold triggered",
    ) -> ScalingPlan:
        action = ScalingAction(
            target_resource_id=resource_id,
            direction=direction,
            delta_units=delta_units,
            reason=reason,
        )
        plan = ScalingPlan(
            tenant_id=tenant_id,
            resource_id=resource_id,
            direction=direction,
            actions=[action],
        )

        # Delegate execution via DelegationRequest (no direct infrastructure mutation)
        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action=f"scaling_{direction.value.lower()}",
            payload={"resource_id": resource_id, "delta_units": delta_units, "reason": reason},
            requester_id="scaling_manager",
        )
        plan.delegation_id = del_req.delegation_id
        plan.status = ScalingStatus.DELEGATED

        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> ScalingPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ResilienceResourceNotFoundException(plan_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, plan.tenant_id)

        return plan
