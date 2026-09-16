"""Tenant-Scoped Architecture Analytics & Reporting Engine."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.architecture_platform.dependencies import DependencyManager
from app.architecture_platform.nodes import ArchitectureNodeManager
from app.architecture_platform.resilience import ResilienceAnalyzer
from app.architecture_platform.trust import ArchitectureTrustEngine


class ArchitectureInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"ins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    severity: str = "MEDIUM"


class ArchitectureReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"archrep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    architecture_complexity_score: float = 45.0
    total_nodes_count: int = 0
    total_dependencies_count: int = 0
    detected_cycles_count: int = 0
    spof_count: int = 0
    drift_count: int = 0
    resilience_score: float = 85.0
    trust_score: float = 90.0
    change_success_rate_pct: float = 98.5
    insights: List[ArchitectureInsight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureAnalyticsEngine:
    """Generates tenant-isolated architecture intelligence reports."""

    def __init__(
        self,
        node_manager: ArchitectureNodeManager,
        dependency_manager: DependencyManager,
        resilience_analyzer: ResilienceAnalyzer,
        trust_engine: ArchitectureTrustEngine,
    ) -> None:
        self.node_manager = node_manager
        self.dependency_manager = dependency_manager
        self.resilience_analyzer = resilience_analyzer
        self.trust_engine = trust_engine

    def generate_report(self, tenant_id: str) -> ArchitectureReport:
        nodes = self.node_manager.list_nodes(tenant_id=tenant_id)
        deps = self.dependency_manager.list_dependencies(tenant_id=tenant_id)
        cycles = self.dependency_manager.detect_cycles(tenant_id=tenant_id)

        res_eval = self.resilience_analyzer.evaluate_resilience(tenant_id=tenant_id)
        trust = self.trust_engine.get_trust_score(tenant_id=tenant_id)

        insights = []
        if len(cycles) > 0:
            insights.append(
                ArchitectureInsight(
                    title="Cyclic Dependency Detected",
                    description=f"Found {len(cycles)} cyclic dependency loop(s). Review graph to prevent deadlock risks.",
                    severity="HIGH",
                )
            )

        if res_eval.has_critical_spof:
            insights.append(
                ArchitectureInsight(
                    title="Single Point of Failure (SPOF)",
                    description=f"Identified {len(res_eval.spofs)} critical single point(s) of failure.",
                    severity="CRITICAL",
                )
            )

        complexity = (len(nodes) * 1.5) + (len(deps) * 2.0)

        return ArchitectureReport(
            tenant_id=tenant_id,
            architecture_complexity_score=complexity,
            total_nodes_count=len(nodes),
            total_dependencies_count=len(deps),
            detected_cycles_count=len(cycles),
            spof_count=len(res_eval.spofs),
            resilience_score=res_eval.resilience_score,
            trust_score=trust.overall_score,
            insights=insights,
        )
