"""Cross-Domain Dependency Intelligence Engine for Phase 5.51 Enterprise AI Unified Intelligence."""

import uuid
from typing import Dict, List, Optional, Set

from pydantic import BaseModel

from app.unified_intelligence.domains import IntelligenceDomain


class DependencyNode(BaseModel):
    node_id: str
    domain: IntelligenceDomain
    entity_id: str
    entity_name: str


class DependencyEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str = "DEPENDS_ON"  # DEPENDS_ON, USES, AUTHORIZES, GOVERNS
    weight: float = 1.0


class CrossDomainDependencyGraph:
    """Analytical graph mapping cross-domain dependencies."""

    def __init__(self, graph_id: Optional[str] = None, tenant_id: str = "default_tenant") -> None:
        self.graph_id = graph_id or f"graph-{uuid.uuid4().hex[:8]}"
        self.tenant_id = tenant_id
        self._nodes: Dict[str, DependencyNode] = {}
        self._edges: List[DependencyEdge] = []

    def add_node(self, node_id: str, domain: IntelligenceDomain, entity_id: str, entity_name: str) -> DependencyNode:
        node = DependencyNode(node_id=node_id, domain=domain, entity_id=entity_id, entity_name=entity_name)
        self._nodes[node_id] = node
        return node

    def add_edge(
        self, source_node_id: str, target_node_id: str, relationship_type: str = "DEPENDS_ON"
    ) -> DependencyEdge:
        edge = DependencyEdge(
            source_node_id=source_node_id, target_node_id=target_node_id, relationship_type=relationship_type
        )
        self._edges.append(edge)
        return edge

    def get_downstream_dependencies(self, entry_node_id: str) -> List[str]:
        visited: Set[str] = set()
        queue = [entry_node_id]

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            for edge in self._edges:
                if edge.source_node_id == curr and edge.target_node_id not in visited:
                    queue.append(edge.target_node_id)

        visited.discard(entry_node_id)
        return list(visited)


# Alias for backward compatibility
DependencyGraph = CrossDomainDependencyGraph


class DependencyIntelligenceEngine:
    """Engine for building and querying cross-domain dependency graphs."""

    def __init__(self) -> None:
        pass

    def build_graph(self, tenant_id: str) -> CrossDomainDependencyGraph:
        return CrossDomainDependencyGraph(tenant_id=tenant_id)
