"""Architecture Resilience & SPOF Analysis Subsystem."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.architecture_platform.dependencies import DependencyManager


class SinglePointOfFailure(BaseModel):
    spof_id: str = Field(default_factory=lambda: f"spof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    node_id: str
    node_name: str
    in_degree_count: int
    cascading_risk_severity: str = "HIGH"
    recommendation: str = "Introduce redundant service replica or fallback route."


class FailureScenario(BaseModel):
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    impacted_nodes_count: int


class ArchitectureResilienceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"res_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resilience_score: float  # 0.0 - 100.0
    spofs: List[SinglePointOfFailure] = Field(default_factory=list)
    has_critical_spof: bool = False
    recommendations: List[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceAnalyzer:
    """Analyzes architecture graph resilience, single points of failure, and cascading risks."""

    def __init__(self, dependency_manager: DependencyManager) -> None:
        self.dependency_manager = dependency_manager

    def evaluate_resilience(self, tenant_id: str) -> ArchitectureResilienceAssessment:
        concentration = self.dependency_manager.calculate_dependency_concentration(tenant_id)
        high_in_nodes = concentration.get("high_in_degree_nodes", [])

        spofs: List[SinglePointOfFailure] = []
        recommendations = []

        for node_id, count in high_in_nodes:
            if count >= 3:
                spof = SinglePointOfFailure(
                    tenant_id=tenant_id,
                    node_id=node_id,
                    node_name=f"Node {node_id}",
                    in_degree_count=count,
                    cascading_risk_severity="HIGH" if count >= 5 else "MEDIUM",
                    recommendation=f"Decouple node '{node_id}' or add load balanced fallback.",
                )
                spofs.append(spof)
                recommendations.append(spof.recommendation)

        has_critical = any(s.cascading_risk_severity == "HIGH" for s in spofs)

        # Base resilience score calculation
        base_score = 100.0 - (len(spofs) * 15.0)
        resilience_score = max(0.0, min(100.0, base_score))

        return ArchitectureResilienceAssessment(
            tenant_id=tenant_id,
            resilience_score=resilience_score,
            spofs=spofs,
            has_critical_spof=has_critical,
            recommendations=recommendations,
        )
