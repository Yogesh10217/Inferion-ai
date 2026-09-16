"""Integration Dependency Intelligence (Phase 5.40)."""

import uuid
from enum import Enum
from typing import Dict, List, Set

from pydantic import BaseModel, Field


class DependencyImpact(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL_PATH = "CRITICAL_PATH"


class DependencyNode(BaseModel):
    node_id: str
    tenant_id: str
    node_type: str  # CONNECTOR, WORKFLOW, ENDPOINT, SYSTEM
    name: str


class DependencyEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: f"dep_edge_{uuid.uuid4().hex[:8]}")
    source_node_id: str
    target_node_id: str
    impact: DependencyImpact = DependencyImpact.MEDIUM


class IntegrationDependency(BaseModel):
    dependency_id: str = Field(default_factory=lambda: f"dep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source_system_id: str
    target_system_id: str
    impact: DependencyImpact = DependencyImpact.MEDIUM


class IntegrationDependencyGraph(BaseModel):
    tenant_id: str
    nodes: Dict[str, DependencyNode] = Field(default_factory=dict)
    edges: List[DependencyEdge] = Field(default_factory=list)


class IntegrationDependencyManager:
    """Manages integration dependency mapping and impact analysis."""

    def __init__(self) -> None:
        self._graphs: Dict[str, IntegrationDependencyGraph] = {}

    def get_or_create_graph(self, tenant_id: str) -> IntegrationDependencyGraph:
        if tenant_id not in self._graphs:
            self._graphs[tenant_id] = IntegrationDependencyGraph(tenant_id=tenant_id)
        return self._graphs[tenant_id]

    def add_dependency(
        self,
        tenant_id: str,
        source_system_id: str,
        target_system_id: str,
        impact: DependencyImpact = DependencyImpact.MEDIUM,
    ) -> IntegrationDependency:
        graph = self.get_or_create_graph(tenant_id)

        src_node = DependencyNode(node_id=source_system_id, tenant_id=tenant_id, node_type="SYSTEM", name=source_system_id)
        tgt_node = DependencyNode(node_id=target_system_id, tenant_id=tenant_id, node_type="SYSTEM", name=target_system_id)

        graph.nodes[source_system_id] = src_node
        graph.nodes[target_system_id] = tgt_node

        edge = DependencyEdge(source_node_id=source_system_id, target_node_id=target_system_id, impact=impact)
        graph.edges.append(edge)

        return IntegrationDependency(
            tenant_id=tenant_id,
            source_system_id=source_system_id,
            target_system_id=target_system_id,
            impact=impact,
        )

    def analyze_impact(self, tenant_id: str, failed_system_id: str) -> List[str]:
        graph = self.get_or_create_graph(tenant_id)
        impacted: Set[str] = set()

        def dfs(current_id: str):
            for edge in graph.edges:
                if edge.source_node_id == current_id and edge.target_node_id not in impacted:
                    impacted.add(edge.target_node_id)
                    dfs(edge.target_node_id)

        dfs(failed_system_id)
        return list(impacted)
