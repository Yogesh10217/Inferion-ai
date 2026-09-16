"""Multi-Region Resilience Intelligence Subsystem (Phase 5.37)."""

import uuid
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard


class RegionalStrategy(str, Enum):
    ACTIVE_ACTIVE = "ACTIVE_ACTIVE"
    ACTIVE_PASSIVE = "ACTIVE_PASSIVE"
    WARM_STANDBY = "WARM_STANDBY"
    COLD_STANDBY = "COLD_STANDBY"


class RegionHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    OUTAGE = "OUTAGE"
    UNKNOWN = "UNKNOWN"


class RegionReference(BaseModel):
    region_id: str
    region_name: str
    is_primary: bool = True
    health: RegionHealth = RegionHealth.HEALTHY


class RegionCapacity(BaseModel):
    region_id: str
    available_capacity_pct: float = 100.0


class RegionalResiliencePlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"regplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    strategy: RegionalStrategy = RegionalStrategy.ACTIVE_PASSIVE
    primary_region: str = "us-east-1"
    secondary_regions: List[str] = Field(default_factory=lambda: ["us-west-2"])


class RegionalFailoverAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"regeval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    is_failover_recommended: bool = False
    recommended_target_region: Optional[str] = None
    reason: str = "Primary region is healthy"


class RegionalResilienceManager:
    """Multi-Region Resilience Intelligence Manager coordinating cross-region strategies without leaking infrastructure topology."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._region_health: Dict[str, RegionHealth] = {
            "us-east-1": RegionHealth.HEALTHY,
            "us-west-2": RegionHealth.HEALTHY,
            "eu-west-1": RegionHealth.HEALTHY,
        }

    def set_region_health(self, region_id: str, health: RegionHealth) -> None:
        self._region_health[region_id] = health

    def evaluate_regional_resilience(
        self,
        tenant_id: str,
        service_id: str,
        primary_region: str = "us-east-1",
        secondary_region: str = "us-west-2",
    ) -> RegionalFailoverAssessment:
        p_health = self._region_health.get(primary_region, RegionHealth.HEALTHY)
        s_health = self._region_health.get(secondary_region, RegionHealth.HEALTHY)

        if p_health == RegionHealth.OUTAGE and s_health == RegionHealth.HEALTHY:
            return RegionalFailoverAssessment(
                tenant_id=tenant_id,
                service_id=service_id,
                is_failover_recommended=True,
                recommended_target_region=secondary_region,
                reason=f"Primary region '{primary_region}' is in OUTAGE state; secondary region '{secondary_region}' is HEALTHY.",
            )

        return RegionalFailoverAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            is_failover_recommended=False,
            recommended_target_region=None,
            reason=f"Primary region '{primary_region}' health status is '{p_health.value}'.",
        )
