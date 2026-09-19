"""Service Catalog & Dependency Graph Management."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from app.platform_operations.exceptions import ServiceNotFoundException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ServiceTier(str, Enum):
    TIER_0_CRITICAL = "TIER_0_CRITICAL"
    TIER_1_HIGH = "TIER_1_HIGH"
    TIER_2_MEDIUM = "TIER_2_MEDIUM"
    TIER_3_LOW = "TIER_3_LOW"


class ServiceHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class ServiceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    DEPRECATED = "DEPRECATED"
    INACTIVE = "INACTIVE"


class ServiceDependencyType(str, Enum):
    UPSTREAM = "UPSTREAM"
    DOWNSTREAM = "DOWNSTREAM"
    TRANSITIVE = "TRANSITIVE"


class ServiceDependency(BaseModel):
    """Relationship between services."""

    dependency_id: str = Field(default_factory=lambda: f"dep_{uuid.uuid4().hex[:10]}")
    source_service_id: str
    target_service_id: str
    tenant_id: str = "global"
    dependency_type: ServiceDependencyType = ServiceDependencyType.UPSTREAM
    is_critical: bool = True
    description: str = ""
    created_at: datetime = Field(default_factory=_now)


class Service(BaseModel):
    """Operational service definition."""

    service_id: str = Field(default_factory=lambda: f"svc_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    name: str
    description: str = ""
    service_tier: ServiceTier = ServiceTier.TIER_1_HIGH
    health: ServiceHealth = ServiceHealth.HEALTHY
    status: ServiceStatus = ServiceStatus.ACTIVE
    owner_team: str = "platform-engineering"
    operational_contact: str = "ops@organization.com"
    slo_ids: List[str] = Field(default_factory=list)
    resource_references: List[str] = Field(default_factory=list)  # Linked ControlPlane resources
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ServiceCatalogManager:
    """Manages tenant-aware service inventory and dependency graph resolution."""

    def __init__(self) -> None:
        self._services: Dict[str, Service] = {}
        self._dependencies: Dict[str, ServiceDependency] = {}

    def register_service(
        self,
        tenant_id: str,
        name: str,
        service_tier: ServiceTier = ServiceTier.TIER_1_HIGH,
        description: str = "",
        owner_team: str = "platform-engineering",
        operational_contact: str = "ops@organization.com",
        slo_ids: Optional[List[str]] = None,
        resource_references: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Service:
        svc = Service(
            tenant_id=tenant_id,
            name=name,
            service_tier=service_tier,
            description=description,
            owner_team=owner_team,
            operational_contact=operational_contact,
            slo_ids=slo_ids or [],
            resource_references=resource_references or [],
            metadata=metadata or {},
        )
        self._services[svc.service_id] = svc
        logger.info(f"[SERVICE CATALOG] Registered service '{svc.name}' ({svc.service_id}) for tenant '{tenant_id}'")
        return svc

    def get_service(self, service_id: str, tenant_id: str) -> Service:
        if service_id not in self._services:
            raise ServiceNotFoundException(f"Service '{service_id}' not found.")
        svc = self._services[service_id]
        if svc.tenant_id not in (tenant_id, "global"):
            raise ServiceNotFoundException(f"Service '{service_id}' not accessible by tenant '{tenant_id}'.")
        return svc

    def update_service_health(self, service_id: str, tenant_id: str, health: ServiceHealth) -> Service:
        svc = self.get_service(service_id, tenant_id)
        svc.health = health
        svc.updated_at = _now()
        logger.info(f"[SERVICE CATALOG] Updated health for service '{service_id}' to {health.value}")
        return svc

    def list_services(self, tenant_id: str) -> List[Service]:
        return [s for s in self._services.values() if s.tenant_id in (tenant_id, "global")]

    def add_dependency(
        self,
        tenant_id: str,
        source_service_id: str,
        target_service_id: str,
        dependency_type: ServiceDependencyType = ServiceDependencyType.UPSTREAM,
        is_critical: bool = True,
        description: str = "",
    ) -> ServiceDependency:
        # Validate services exist
        self.get_service(source_service_id, tenant_id)
        self.get_service(target_service_id, tenant_id)

        dep = ServiceDependency(
            tenant_id=tenant_id,
            source_service_id=source_service_id,
            target_service_id=target_service_id,
            dependency_type=dependency_type,
            is_critical=is_critical,
            description=description,
        )
        self._dependencies[dep.dependency_id] = dep
        logger.info(
            f"[SERVICE CATALOG] Added dependency: {source_service_id} -> {target_service_id} ({dependency_type.value})"
        )
        return dep

    def resolve_dependencies(
        self,
        service_id: str,
        tenant_id: str,
        direction: ServiceDependencyType = ServiceDependencyType.UPSTREAM,
        transitive: bool = True,
    ) -> List[Service]:
        """Resolve upstream or downstream services for a given service."""
        self.get_service(service_id, tenant_id)
        visited: Set[str] = set()
        to_visit = [service_id]

        resolved_ids: Set[str] = set()

        while to_visit:
            curr = to_visit.pop(0)
            if curr in visited:
                continue
            visited.add(curr)

            for dep in self._dependencies.values():
                if dep.tenant_id not in (tenant_id, "global"):
                    continue

                if direction == ServiceDependencyType.UPSTREAM:
                    # Upstream: target service that curr depends on
                    if dep.source_service_id == curr and dep.target_service_id not in visited:
                        resolved_ids.add(dep.target_service_id)
                        if transitive:
                            to_visit.append(dep.target_service_id)
                else:
                    # Downstream: source service that depends on curr
                    if dep.target_service_id == curr and dep.source_service_id not in visited:
                        resolved_ids.add(dep.source_service_id)
                        if transitive:
                            to_visit.append(dep.source_service_id)

        return [self._services[sid] for sid in resolved_ids if sid in self._services]
