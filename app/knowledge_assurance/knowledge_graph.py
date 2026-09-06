"""Analytical knowledge graph traversal across platform domains."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import CrossTenantKnowledgeAssuranceException


class KnowledgeRelationship(str, Enum):
    REFERENCES = "REFERENCES"
    GOVERNS = "GOVERNS"
    ENFORCES = "ENFORCES"
    IMPACTS = "IMPACTS"
    DERIVED_FROM = "DERIVED_FROM"
    DEPENDS_ON = "DEPENDS_ON"
    CONTRADICTS = "CONTRADICTS"


class KnowledgeGraphNode(BaseModel):
    node_id: str
    node_type: str  # DECISION, MODEL, DATASET, CONTROL, INCIDENT, SERVICE, POLICY, WORKFLOW, KNOWLEDGE
    name: str
    tenant_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_node_id: str
    target_node_id: str
    relationship: KnowledgeRelationship = KnowledgeRelationship.REFERENCES
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeTraversal(BaseModel):
    start_node_id: str
    max_depth: int = 3
    visited_nodes: List[KnowledgeGraphNode] = Field(default_factory=list)
    traversed_edges: List[KnowledgeGraphEdge] = Field(default_factory=list)


class KnowledgeGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    nodes: Dict[str, KnowledgeGraphNode] = Field(default_factory=dict)
    edges: List[KnowledgeGraphEdge] = Field(default_factory=list)


class KnowledgeGraphManager:
    """Manages analytical traversal and dependency mapping across enterprise knowledge entities."""

    def __init__(self) -> None:
        self._graphs: Dict[str, KnowledgeGraph] = {}

    def get_or_create_graph(self, tenant_id: str) -> KnowledgeGraph:
        if tenant_id not in self._graphs:
            self._graphs[tenant_id] = KnowledgeGraph(tenant_id=tenant_id)
        return self._graphs[tenant_id]

    def add_node(self, tenant_id: str, node: KnowledgeGraphNode) -> KnowledgeGraphNode:
        if node.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        graph = self.get_or_create_graph(tenant_id)
        graph.nodes[node.node_id] = node
        return node

    def add_edge(self, tenant_id: str, edge: KnowledgeGraphEdge) -> KnowledgeGraphEdge:
        graph = self.get_or_create_graph(tenant_id)
        graph.edges.append(edge)
        return edge

    def traverse(self, tenant_id: str, start_node_id: str, max_depth: int = 3) -> KnowledgeTraversal:
        graph = self.get_or_create_graph(tenant_id)
        start_node = graph.nodes.get(start_node_id)
        if not start_node or start_node.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()

        visited = [start_node]
        edges = []
        for e in graph.edges:
            if e.source_node_id == start_node_id and e.target_node_id in graph.nodes:
                visited.append(graph.nodes[e.target_node_id])
                edges.append(e)

        return KnowledgeTraversal(
            start_node_id=start_node_id,
            max_depth=max_depth,
            visited_nodes=visited,
            traversed_edges=edges,
        )
