"""Controlled Load Shedding Governance Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException, ResilienceResourceNotFoundException


class LoadSheddingPriority(int, Enum):
    P0_CRITICAL = 0
    P1_HIGH = 1
    P2_MEDIUM = 2
    P3_LOW = 3


class LoadSheddingStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    INACTIVE = "INACTIVE"


class LoadSheddingRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"shedrule_{uuid.uuid4().hex[:12]}")
    workload_name: str
    priority: LoadSheddingPriority = LoadSheddingPriority.P3_LOW
    shed_percentage: float = 100.0


class LoadSheddingPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"shedpoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    rules: List[LoadSheddingRule] = Field(default_factory=list)


class LoadSheddingPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"shedplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_service_id: str
    shedding_targets: List[str] = Field(default_factory=list)  # Low priority shed first
    protected_workloads: List[str] = Field(default_factory=list)  # Critical workloads protected
    status: LoadSheddingStatus = LoadSheddingStatus.PLANNED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LoadSheddingManager:
    """Controlled Load Shedding Governance Manager.

    Protects critical workloads by shedding low-priority workloads first under overload.
    """

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, LoadSheddingPlan] = {}

    def formulate_shedding_plan(
        self,
        tenant_id: str,
        target_service_id: str,
        workloads: List[Dict[str, Any]],  # List of {"name": str, "priority": int}
    ) -> LoadSheddingPlan:
        # Sort workloads by priority descending (higher integer = lower priority = shed first)
        sorted_workloads = sorted(workloads, key=lambda w: w.get("priority", 3), reverse=True)

        shed_targets = [w["name"] for w in sorted_workloads if w.get("priority", 3) >= 2]
        protected = [w["name"] for w in sorted_workloads if w.get("priority", 3) < 2]

        plan = LoadSheddingPlan(
            tenant_id=tenant_id,
            target_service_id=target_service_id,
            shedding_targets=shed_targets,
            protected_workloads=protected,
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> LoadSheddingPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ResilienceResourceNotFoundException(plan_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, plan.tenant_id)

        return plan
