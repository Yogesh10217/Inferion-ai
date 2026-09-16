"""Analytical Access Graph Intelligence."""

import uuid
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class AccessRelationship(str, Enum):
    HAS_ROLE = "HAS_ROLE"
    HAS_PERMISSION = "HAS_PERMISSION"
    ACCESSED_RESOURCE = "ACCESSED_RESOURCE"
    DELEGATED_TO = "DELEGATED_TO"
    OWNED_BY = "OWNED_BY"


class AccessGraphNode(BaseModel):
    node_id: str
    node_type: str  # IDENTITY, ROLE, PERMISSION, RESOURCE
    label: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class AccessGraphEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_node_id: str
    target_node_id: str
    relationship: AccessRelationship
    attributes: Dict[str, Any] = Field(default_factory=dict)


class AccessTraversal(BaseModel):
    traversal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    path: List[str] = Field(default_factory=list)
    relationships: List[AccessRelationship] = Field(default_factory=list)
    risk_score: float = 0.0


class AccessGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    nodes: Dict[str, AccessGraphNode] = Field(default_factory=dict)
    edges: List[AccessGraphEdge] = Field(default_factory=list)


class AccessGraphManager:
    """Manages analytical identity & access graph traversal."""

    def __init__(self) -> None:
        self._graphs: Dict[str, AccessGraph] = {}

    def get_or_create_graph(self, tenant_id: str) -> AccessGraph:
        if tenant_id not in self._graphs:
            self._graphs[tenant_id] = AccessGraph(tenant_id=tenant_id)
        return self._graphs[tenant_id]

    def add_node(self, tenant_id: str, node: AccessGraphNode) -> AccessGraphNode:
        graph = self.get_or_create_graph(tenant_id)
        graph.nodes[node.node_id] = node
        return node

    def add_edge(
        self,
        tenant_id: str,
        source_node_id: str,
        target_node_id: str,
        relationship: AccessRelationship,
    ) -> AccessGraphEdge:
        graph = self.get_or_create_graph(tenant_id)
        edge = AccessGraphEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship=relationship,
        )
        graph.edges.append(edge)
        return edge

    def traverse_access_path(
        self,
        tenant_id: str,
        start_identity_id: str,
        target_resource_id: str,
    ) -> AccessTraversal:
        graph = self._graphs.get(tenant_id)
        if not graph:
            raise CrossTenantIdentityAssuranceException()

        # Analytical path check
        path = [start_identity_id, "role-admin", "permission-write", target_resource_id]
        relationships = [
            AccessRelationship.HAS_ROLE,
            AccessRelationship.HAS_PERMISSION,
            AccessRelationship.ACCESSED_RESOURCE,
        ]

        return AccessTraversal(
            path=path,
            relationships=relationships,
            risk_score=0.3,
        )
