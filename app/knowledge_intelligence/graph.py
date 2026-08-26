"""Cross-Platform Knowledge Graph Subsystem (Phase 5.35)."""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeGraphException,
)
from app.knowledge_intelligence.relationships import KnowledgeRelationship, RelationshipType
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeGraphNode(BaseModel):
    node_id: str
    tenant_id: str
    label: str
    node_type: str = "KNOWLEDGE_ITEM"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(BaseModel):
    edge_id: str
    tenant_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: RelationshipType
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphTraversal(BaseModel):
    start_node_id: str
    depth: int = 2
    direction: str = "BOTH"  # UPSTREAM, DOWNSTREAM, BOTH


class GraphTraversalResult(BaseModel):
    start_node_id: str
    visited_node_ids: List[str]
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]


class KnowledgeGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"kgraph_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    nodes: Dict[str, KnowledgeGraphNode] = Field(default_factory=dict)
    edges: Dict[str, KnowledgeGraphEdge] = Field(default_factory=dict)


class KnowledgeGraphManager:
    """Manages multi-tenant knowledge graph structures storing references and safe metadata only."""

    def __init__(self) -> None:
        self._graphs: Dict[str, KnowledgeGraph] = {}

    def get_or_create_graph(self, tenant_id: str) -> KnowledgeGraph:
        if tenant_id not in self._graphs:
            self._graphs[tenant_id] = KnowledgeGraph(tenant_id=tenant_id)
        return self._graphs[tenant_id]

    def add_node(self, tenant_id: str, node_id: str, label: str, node_type: str = "KNOWLEDGE_ITEM", metadata: Optional[Dict[str, Any]] = None) -> KnowledgeGraphNode:
        graph = self.get_or_create_graph(tenant_id)
        sanitized_meta = SensitiveDataSanitizer.sanitize(metadata or {})
        node = KnowledgeGraphNode(
            node_id=node_id,
            tenant_id=tenant_id,
            label=label,
            node_type=node_type,
            metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
        )
        graph.nodes[node_id] = node
        return node

    def add_edge(self, tenant_id: str, relationship: KnowledgeRelationship) -> KnowledgeGraphEdge:
        if relationship.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAccessException(tenant_id)
        graph = self.get_or_create_graph(tenant_id)
        
        if relationship.source_id not in graph.nodes:
            self.add_node(tenant_id, relationship.source_id, f"Node_{relationship.source_id}")
        if relationship.target_id not in graph.nodes:
            self.add_node(tenant_id, relationship.target_id, f"Node_{relationship.target_id}")

        edge = KnowledgeGraphEdge(
            edge_id=relationship.relationship_id,
            tenant_id=tenant_id,
            source_node_id=relationship.source_id,
            target_node_id=relationship.target_id,
            relationship_type=relationship.relationship_type,
            metadata=relationship.metadata,
        )
        graph.edges[edge.edge_id] = edge
        return edge

    def traverse(self, tenant_id: str, start_node_id: str, depth: int = 2, direction: str = "BOTH") -> GraphTraversalResult:
        graph = self.get_or_create_graph(tenant_id)
        if start_node_id not in graph.nodes:
            # Check cross-tenant leak
            for other_tid, other_g in self._graphs.items():
                if other_tid != tenant_id and start_node_id in other_g.nodes:
                    raise CrossTenantKnowledgeAccessException(tenant_id)

        visited_nodes: Set[str] = set()
        visited_edges: Set[str] = set()
        queue = [(start_node_id, 0)]

        while queue:
            curr_id, curr_depth = queue.pop(0)
            if curr_id in visited_nodes or curr_depth > depth:
                continue
            visited_nodes.add(curr_id)

            for edge in graph.edges.values():
                if direction in ("DOWNSTREAM", "BOTH") and edge.source_node_id == curr_id:
                    visited_edges.add(edge.edge_id)
                    if edge.target_node_id not in visited_nodes:
                        queue.append((edge.target_node_id, curr_depth + 1))
                if direction in ("UPSTREAM", "BOTH") and edge.target_node_id == curr_id:
                    visited_edges.add(edge.edge_id)
                    if edge.source_node_id not in visited_nodes:
                        queue.append((edge.source_node_id, curr_depth + 1))

        ret_nodes = [graph.nodes[nid] for nid in visited_nodes if nid in graph.nodes]
        ret_edges = [graph.edges[eid] for eid in visited_edges if eid in graph.edges]

        return GraphTraversalResult(
            start_node_id=start_node_id,
            visited_node_ids=list(visited_nodes),
            nodes=ret_nodes,
            edges=ret_edges,
        )
