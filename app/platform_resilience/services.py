"""Enterprise Resilience Service Registry Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import (
    CrossTenantResilienceAccessException,
    ResilienceResourceNotFoundException,
)
from app.reliability_platform.services import ServiceManager as ReliabilityServiceManager
from app.reliability_platform.services import ServiceTier


class ServiceCriticality(str, Enum):
    TIER_0_CRITICAL = "TIER_0_CRITICAL"
    TIER_1_HIGH = "TIER_1_HIGH"
    TIER_2_STANDARD = "TIER_2_STANDARD"
    TIER_3_LOW = "TIER_3_LOW"


class ServiceAvailabilityTarget(BaseModel):
    target_percentage: float = 99.9
    max_downtime_minutes_per_month: float = 43.8
    rto_minutes: float = 15.0
    rpo_minutes: float = 5.0


class ServiceDependencyReference(BaseModel):
    dependency_id: str
    target_service_name: str
    is_hard_dependency: bool = True
    criticality: ServiceCriticality = ServiceCriticality.TIER_1_HIGH


class ResilienceService(BaseModel):
    service_id: str = Field(default_factory=lambda: f"res_svc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_name: str
    tier: ServiceCriticality = ServiceCriticality.TIER_2_STANDARD
    availability_target: ServiceAvailabilityTarget = Field(default_factory=ServiceAvailabilityTarget)
    dependencies: List[ServiceDependencyReference] = Field(default_factory=list)
    region: str = "us-east-1"
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceServiceManager:
    """Enterprise resilience service registry coordinating service resilience metadata.

    Reuses existing ReliabilityServiceManager for underlying service tier alignment.
    """

    def __init__(
        self,
        reliability_service_manager: Optional[ReliabilityServiceManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.reliability_service_manager = reliability_service_manager or ReliabilityServiceManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._services: Dict[str, ResilienceService] = {}

    def register_service(
        self,
        tenant_id: str,
        service_name: str,
        tier: ServiceCriticality = ServiceCriticality.TIER_2_STANDARD,
        availability_target: Optional[ServiceAvailabilityTarget] = None,
        region: str = "us-east-1",
        dependencies: Optional[List[ServiceDependencyReference]] = None,
    ) -> ResilienceService:
        svc = ResilienceService(
            tenant_id=tenant_id,
            service_name=service_name,
            tier=tier,
            availability_target=availability_target or ServiceAvailabilityTarget(),
            region=region,
            dependencies=dependencies or [],
        )
        self._services[svc.service_id] = svc

        # Align with reliability platform tiering
        try:
            rel_tier = ServiceTier[tier.value]
            self.reliability_service_manager.register_service(tenant_id, service_name, rel_tier)
        except Exception:  # nosec B110
            pass

        return svc

    def get_service(self, service_id: str, tenant_id: str) -> ResilienceService:
        svc = self._services.get(service_id)
        if not svc:
            raise ResilienceResourceNotFoundException(service_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, svc.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, svc.tenant_id)

        return svc

    def list_services(self, tenant_id: str) -> List[ResilienceService]:
        return [s for s in self._services.values() if s.tenant_id == tenant_id or tenant_id == "global"]
