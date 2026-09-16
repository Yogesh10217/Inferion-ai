"""Blast Radius & Change Impact Analysis Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.architecture_platform.dependencies import DependencyManager


class ImpactSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ImpactArea(str, Enum):
    APPLICATION = "APPLICATION"
    SERVICE = "SERVICE"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    MODEL = "MODEL"
    KNOWLEDGE = "KNOWLEDGE"
    DATA_ASSET = "DATA_ASSET"
    INTEGRATION = "INTEGRATION"
    API = "API"
    SECURITY = "SECURITY"
    GOVERNANCE = "GOVERNANCE"
    COST = "COST"
    LATENCY = "LATENCY"
    RELIABILITY = "RELIABILITY"
    RESILIENCE = "RESILIENCE"
    COMPLIANCE = "COMPLIANCE"


class BlastRadius(BaseModel):
    directly_affected_nodes: List[str] = Field(default_factory=list)
    transitively_affected_nodes: List[str] = Field(default_factory=list)
    total_affected_count: int = 0
    impacted_areas: List[ImpactArea] = Field(default_factory=list)
    estimated_severity: ImpactSeverity = ImpactSeverity.MEDIUM


class ImpactAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"impact_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_node_id: str
    action_type: str
    blast_radius: BlastRadius
    estimated_cost_impact_usd: float = 0.0
    reliability_risk: str = "LOW"
    confidence_score: float = 90.0
    evidence: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


ArchitectureImpact = ImpactAnalysis


class ImpactAnalyzer:
    """Analyzes transitive blast radius and multidimensional change impact."""

    def __init__(self, dependency_manager: DependencyManager) -> None:
        self.dependency_manager = dependency_manager

    def analyze_impact(self, tenant_id: str, target_node_id: str, action_type: str = "MODIFY") -> ImpactAnalysis:
        # 1. Transitive downstream blast radius
        downstream = self.dependency_manager.get_transitive_downstream(tenant_id, target_node_id)
        upstream = self.dependency_manager.get_transitive_upstream(tenant_id, target_node_id)

        direct_nodes = [target_node_id]
        transitive_nodes = list(set(downstream) | set(upstream))
        total_affected = len(direct_nodes) + len(transitive_nodes)

        if total_affected >= 10:
            severity = ImpactSeverity.CRITICAL
        elif total_affected >= 5:
            severity = ImpactSeverity.HIGH
        elif total_affected >= 2:
            severity = ImpactSeverity.MEDIUM
        else:
            severity = ImpactSeverity.LOW

        impacted_areas = [
            ImpactArea.SERVICE,
            ImpactArea.RELIABILITY,
            ImpactArea.COST,
            ImpactArea.GOVERNANCE,
        ]

        blast = BlastRadius(
            directly_affected_nodes=direct_nodes,
            transitively_affected_nodes=transitive_nodes,
            total_affected_count=total_affected,
            impacted_areas=impacted_areas,
            estimated_severity=severity,
        )

        evidence = [
            f"Direct target node: {target_node_id}",
            f"Transitively downstream node count: {len(transitive_nodes)}",
            f"Transitively upstream dependency count: {len(upstream)}",
        ]

        return ImpactAnalysis(
            tenant_id=tenant_id,
            target_node_id=target_node_id,
            action_type=action_type,
            blast_radius=blast,
            estimated_cost_impact_usd=10.0 * total_affected,
            reliability_risk="HIGH" if severity in (ImpactSeverity.HIGH, ImpactSeverity.CRITICAL) else "LOW",
            confidence_score=95.0,
            evidence=evidence,
        )
