"""Operational Impact Analysis Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.platform_operations.services import ServiceCatalogManager, ServiceDependencyType, ServiceTier

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ImpactScope(str, Enum):
    SERVICE_LOCAL = "SERVICE_LOCAL"
    DOWNSTREAM_CASCADE = "DOWNSTREAM_CASCADE"
    TENANT_WIDE = "TENANT_WIDE"
    CROSS_TENANT_CONTAINED = "CROSS_TENANT_CONTAINED"


class AffectedResource(BaseModel):
    resource_id: str
    resource_type: str
    tenant_id: str
    impact_description: str = ""


class ImpactAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"imp_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    primary_service_id: str
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    impact_scope: ImpactScope = ImpactScope.SERVICE_LOCAL
    affected_services: List[str] = Field(default_factory=list)
    affected_applications: List[str] = Field(default_factory=list)
    affected_workflows: List[str] = Field(default_factory=list)
    affected_agents: List[str] = Field(default_factory=list)
    estimated_blast_radius_score: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class ImpactAnalyzer:
    """Evaluates blast radius and operational impact using service dependency graph."""

    def __init__(self, service_catalog_manager: Optional[ServiceCatalogManager] = None) -> None:
        self.service_catalog_manager = service_catalog_manager or ServiceCatalogManager()

    def assess_impact(
        self,
        tenant_id: str,
        service_id: str,
        affected_applications: Optional[List[str]] = None,
        affected_workflows: Optional[List[str]] = None,
    ) -> ImpactAssessment:
        # Strict tenant boundary verification
        svc = self.service_catalog_manager.get_service(service_id, tenant_id)

        # Resolve downstream dependencies
        downstream = self.service_catalog_manager.resolve_dependencies(
            service_id=service_id,
            tenant_id=tenant_id,
            direction=ServiceDependencyType.DOWNSTREAM,
            transitive=True,
        )

        downstream_ids = [d.service_id for d in downstream]
        all_impacted_svc_ids = [svc.service_id] + downstream_ids

        # Determine ImpactLevel based on ServiceTier and downstream count
        if svc.service_tier == ServiceTier.TIER_0_CRITICAL or len(downstream_ids) >= 3:
            level = ImpactLevel.CRITICAL
            scope = ImpactScope.TENANT_WIDE
        elif svc.service_tier == ServiceTier.TIER_1_HIGH or len(downstream_ids) >= 1:
            level = ImpactLevel.HIGH
            scope = ImpactScope.DOWNSTREAM_CASCADE
        else:
            level = ImpactLevel.MEDIUM
            scope = ImpactScope.SERVICE_LOCAL

        blast_radius = round(min(1.0, 0.2 + (len(downstream_ids) * 0.25)), 2)

        evidence = [
            f"Primary service '{svc.name}' is tier {svc.service_tier.value}.",
            f"Downstream cascade affects {len(downstream_ids)} dependent services.",
        ]

        assessment = ImpactAssessment(
            tenant_id=tenant_id,
            primary_service_id=service_id,
            impact_level=level,
            impact_scope=scope,
            affected_services=all_impacted_svc_ids,
            affected_applications=affected_applications or [],
            affected_workflows=affected_workflows or [],
            estimated_blast_radius_score=blast_radius,
            evidence=evidence,
        )
        logger.info(
            f"[IMPACT ANALYZER] Calculated impact for service {service_id}: {level.value} (Blast radius: {blast_radius})"
        )
        return assessment
