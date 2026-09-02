"""Enterprise Access Graph (Phase 5.39)."""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class AccessGraphNode(BaseModel):
    """Node in the analytical access graph."""
    node_id: str
    tenant_id: str
    node_type: str  # IDENTITY, ROLE, APPLICATION, AGENT, TOOL, SENSITIVE_RESOURCE, DATASET, KNOWLEDGE_SOURCE
    label: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class AccessGraphEdge(BaseModel):
    """Edge in the analytical access graph."""
    edge_id: str = Field(default_factory=lambda: f"edge_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    is_direct: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)


class AccessGraphPath(BaseModel):
    """Path traversed in the access graph."""
    tenant_id: str
    source_node_id: str
    target_node_id: str
    nodes: List[AccessGraphNode] = Field(default_factory=list)
    edges: List[AccessGraphEdge] = Field(default_factory=list)
    path_length: int = 0
    contains_sensitive_target: bool = False


class AccessGraph(BaseModel):
    """Analytical Access Graph Representation."""
    tenant_id: str
    nodes: Dict[str, AccessGraphNode] = Field(default_factory=dict)
    edges: List[AccessGraphEdge] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessGraphTraversal:
    """Helper for graph traversal and reachability analysis."""

    def __init__(self, graph: AccessGraph) -> None:
        self.graph = graph
        self._adj: Dict[str, List[AccessGraphEdge]] = {}
        for edge in graph.edges:
            if edge.source_node_id not in self._adj:
                self._adj[edge.source_node_id] = []
            self._adj[edge.source_node_id].append(edge)

    def find_paths(self, start_node_id: str, end_node_id: str, max_depth: int = 5) -> List[AccessGraphPath]:
        paths: List[AccessGraphPath] = []

        def dfs(current_id: str, current_nodes: List[AccessGraphNode], current_edges: List[AccessGraphEdge], visited: Set[str]):
            if current_id == end_node_id:
                path_obj = AccessGraphPath(
                    tenant_id=self.graph.tenant_id,
                    source_node_id=start_node_id,
                    target_node_id=end_node_id,
                    nodes=list(current_nodes),
                    edges=list(current_edges),
                    path_length=len(current_edges),
                    contains_sensitive_target=current_nodes[-1].node_type == "SENSITIVE_RESOURCE",
                )
                paths.append(path_obj)
                return

            if len(current_edges) >= max_depth:
                return

            for edge in self._adj.get(current_id, []):
                nxt_id = edge.target_node_id
                if nxt_id not in visited and nxt_id in self.graph.nodes:
                    visited.add(nxt_id)
                    current_nodes.append(self.graph.nodes[nxt_id])
                    current_edges.append(edge)
                    dfs(nxt_id, current_nodes, current_edges, visited)
                    current_edges.pop()
                    current_nodes.pop()
                    visited.remove(nxt_id)

        if start_node_id in self.graph.nodes:
            dfs(start_node_id, [self.graph.nodes[start_node_id]], [], {start_node_id})

        return paths


class AccessGraphManager:
    """Manages analytical access graphs for tenants without direct access mutation."""

    def __init__(self) -> None:
        self._graphs: Dict[str, AccessGraph] = {}

    def get_or_create_graph(self, tenant_id: str) -> AccessGraph:
        if tenant_id not in self._graphs:
            self._graphs[tenant_id] = AccessGraph(tenant_id=tenant_id)
        return self._graphs[tenant_id]

    def add_node(self, tenant_id: str, node_id: str, node_type: str, label: str, attributes: Optional[Dict[str, Any]] = None) -> AccessGraphNode:
        graph = self.get_or_create_graph(tenant_id)
        node = AccessGraphNode(
            node_id=node_id,
            tenant_id=tenant_id,
            node_type=node_type,
            label=label,
            attributes=attributes or {},
        )
        graph.nodes[node_id] = node
        graph.updated_at = datetime.now(timezone.utc)
        return node

    def add_edge(self, tenant_id: str, source_node_id: str, target_node_id: str, relationship_type: str, is_direct: bool = True) -> AccessGraphEdge:
        graph = self.get_or_create_graph(tenant_id)
        edge = AccessGraphEdge(
            tenant_id=tenant_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            is_direct=is_direct,
        )
        graph.edges.append(edge)
        graph.updated_at = datetime.now(timezone.utc)
        return edge

    def analyze_paths(self, tenant_id: str, start_node_id: str, end_node_id: str) -> List[AccessGraphPath]:
        graph = self.get_or_create_graph(tenant_id)
        traversal = AccessGraphTraversal(graph)
        return traversal.find_paths(start_node_id, end_node_id)
