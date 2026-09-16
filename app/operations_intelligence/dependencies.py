"""Operational Dependency Intelligence (Phase 5.41)."""

import uuid
from enum import Enum
from typing import Dict, List, Set

from pydantic import BaseModel, Field


class DependencyImpact(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL_PATH = "CRITICAL_PATH"


class OperationalDependency(BaseModel):
    dependency_id: str = Field(default_factory=lambda: f"op_dep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    upstream_service_id: str
    downstream_service_id: str
    impact: DependencyImpact = DependencyImpact.MEDIUM


class DependencyFailureAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"dep_an_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    failed_service_id: str
    impacted_services: List[str] = Field(default_factory=list)


class OperationalDependencyManager:
    """Manages operational service dependency graphs and failure impact propagation."""

    def __init__(self) -> None:
        self._dependencies: Dict[str, List[OperationalDependency]] = {}  # tenant_id -> List[OperationalDependency]

    def add_dependency(
        self,
        tenant_id: str,
        upstream_service_id: str,
        downstream_service_id: str,
        impact: DependencyImpact = DependencyImpact.MEDIUM,
    ) -> OperationalDependency:
        if tenant_id not in self._dependencies:
            self._dependencies[tenant_id] = []

        dep = OperationalDependency(
            tenant_id=tenant_id,
            upstream_service_id=upstream_service_id,
            downstream_service_id=downstream_service_id,
            impact=impact,
        )
        self._dependencies[tenant_id].append(dep)
        return dep

    def analyze_failure_impact(self, tenant_id: str, failed_service_id: str) -> DependencyFailureAnalysis:
        deps = self._dependencies.get(tenant_id, [])
        impacted: Set[str] = set()

        def dfs(current_id: str):
            for d in deps:
                if d.upstream_service_id == current_id and d.downstream_service_id not in impacted:
                    impacted.add(d.downstream_service_id)
                    dfs(d.downstream_service_id)

        dfs(failed_service_id)
        return DependencyFailureAnalysis(
            tenant_id=tenant_id,
            failed_service_id=failed_service_id,
            impacted_services=list(impacted),
        )
