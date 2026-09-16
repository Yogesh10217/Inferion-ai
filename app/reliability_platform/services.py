"""Reliability Service Registry & Scope Management Subsystem (Phase 5.31)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.reliability_platform.exceptions import CrossTenantReliabilityAccessException, ServiceNotFoundException


class ServiceTier(str, Enum):
    TIER_0_CRITICAL = "TIER_0_CRITICAL"
    TIER_1_HIGH = "TIER_1_HIGH"
    TIER_2_MEDIUM = "TIER_2_MEDIUM"
    TIER_3_LOW = "TIER_3_LOW"


class ServiceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"
    DEPRECATED = "DEPRECATED"


class ReliabilityService(BaseModel):
    service_id: str = Field(default_factory=lambda: f"svc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    tier: ServiceTier = ServiceTier.TIER_1_HIGH
    status: ServiceStatus = ServiceStatus.ACTIVE
    owner_team: str = "sre_team"
    architecture_node_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceManager:
    """Manages enterprise AI service registrations for reliability tracking."""

    def __init__(self) -> None:
        self._services: Dict[str, ReliabilityService] = {}

    def register_service(
        self,
        tenant_id: str,
        name: str,
        tier: ServiceTier = ServiceTier.TIER_1_HIGH,
        owner_team: str = "sre_team",
        architecture_node_id: Optional[str] = None,
    ) -> ReliabilityService:
        svc = ReliabilityService(
            tenant_id=tenant_id,
            name=name,
            tier=tier,
            owner_team=owner_team,
            architecture_node_id=architecture_node_id,
        )
        self._services[svc.service_id] = svc
        return svc

    def get_service(self, service_id: str, tenant_id: str) -> ReliabilityService:
        svc = self._services.get(service_id)
        if not svc:
            raise ServiceNotFoundException(service_id)
        if tenant_id != "global" and svc.tenant_id != "global" and tenant_id != svc.tenant_id:
            raise CrossTenantReliabilityAccessException(tenant_id, svc.tenant_id)
        return svc

    def list_services(self, tenant_id: str) -> List[ReliabilityService]:
        return [svc for svc in self._services.values() if svc.tenant_id == tenant_id]
