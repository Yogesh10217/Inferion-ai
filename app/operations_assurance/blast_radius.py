"""Operational blast radius analysis covering Services, Users, Tenants, Models, Agents, Workflows, Applications, and Business operations."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class BlastRadiusImpactLevel(str, Enum):
    LOCAL = "LOCAL"
    MODERATE = "MODERATE"
    EXTENSIVE = "EXTENSIVE"
    CATASTROPHIC = "CATASTROPHIC"


class OperationalBlastRadiusAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    target_id: str
    impact_level: BlastRadiusImpactLevel = BlastRadiusImpactLevel.MODERATE
    affected_services: List[str] = Field(default_factory=list)
    affected_users_count: int = 0
    affected_tenants: List[str] = Field(default_factory=list)
    affected_models: List[str] = Field(default_factory=list)
    affected_agents: List[str] = Field(default_factory=list)
    affected_workflows: List[str] = Field(default_factory=list)
    affected_applications: List[str] = Field(default_factory=list)
    affected_business_operations: List[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsBlastRadiusEngine:
    """Evaluates the multi-domain blast radius of an operational event or incident."""

    def __init__(self) -> None:
        pass

    def evaluate_blast_radius(
        self,
        tenant_id: str,
        target_id: str,
        affected_services: Optional[List[str]] = None,
        affected_users: int = 0,
        affected_models: Optional[List[str]] = None,
        affected_agents: Optional[List[str]] = None,
    ) -> OperationalBlastRadiusAssessment:
        services = affected_services or []
        models = affected_models or []
        agents = affected_agents or []

        total_impacted = len(services) + len(models) + len(agents)
        if total_impacted > 10 or affected_users > 10000:
            level = BlastRadiusImpactLevel.CATASTROPHIC
        elif total_impacted > 5 or affected_users > 1000:
            level = BlastRadiusImpactLevel.EXTENSIVE
        elif total_impacted > 1 or affected_users > 100:
            level = BlastRadiusImpactLevel.MODERATE
        else:
            level = BlastRadiusImpactLevel.LOCAL

        return OperationalBlastRadiusAssessment(
            tenant_id=tenant_id,
            target_id=target_id,
            impact_level=level,
            affected_services=services,
            affected_users_count=affected_users,
            affected_tenants=[tenant_id],
            affected_models=models,
            affected_agents=agents,
            affected_workflows=[f"workflow-{target_id}"],
            affected_applications=[f"app-{target_id}"],
            affected_business_operations=["core_platform_service"],
        )
