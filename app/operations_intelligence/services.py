"""Enterprise Operational Service Registry (Phase 5.41)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class ServiceCriticality(str, Enum):
    MISSION_CRITICAL = "MISSION_CRITICAL"
    BUSINESS_CRITICAL = "BUSINESS_CRITICAL"
    IMPORTANT = "IMPORTANT"
    LOW = "LOW"


class ServiceOperationalTier(str, Enum):
    TIER_0 = "TIER_0"
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"


class ServiceHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class OperationalService(BaseModel):
    service_id: str = Field(default_factory=lambda: f"svc_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    owner_team: str
    criticality: ServiceCriticality = ServiceCriticality.BUSINESS_CRITICAL
    tier: ServiceOperationalTier = ServiceOperationalTier.TIER_1
    health_status: ServiceHealthStatus = ServiceHealthStatus.HEALTHY
    dependencies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalServiceManager:
    """Manages operational service registry, health, and metadata."""

    def __init__(self) -> None:
        self._services: Dict[str, OperationalService] = {}

    def register_service(
        self,
        tenant_id: str,
        name: str,
        owner_team: str,
        criticality: ServiceCriticality = ServiceCriticality.BUSINESS_CRITICAL,
        tier: ServiceOperationalTier = ServiceOperationalTier.TIER_1,
        dependencies: Optional[List[str]] = None,
    ) -> OperationalService:
        svc = OperationalService(
            tenant_id=tenant_id,
            name=name,
            owner_team=owner_team,
            criticality=criticality,
            tier=tier,
            dependencies=dependencies or [],
        )
        self._services[svc.service_id] = svc
        return svc

    def update_health(self, tenant_id: str, service_id: str, health_status: ServiceHealthStatus) -> OperationalService:
        svc = self.get_service(tenant_id, service_id)
        svc.health_status = health_status
        svc.updated_at = datetime.now(timezone.utc)
        return svc

    def get_service(self, tenant_id: str, service_id: str) -> OperationalService:
        svc = self._services.get(service_id)
        if not svc or svc.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return svc

    def list_services(self, tenant_id: str) -> List[OperationalService]:
        return [s for s in self._services.values() if s.tenant_id == tenant_id]
