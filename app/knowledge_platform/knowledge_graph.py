"""Knowledge Graph & Relationship Intelligence Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.exceptions import KnowledgeGraphException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeNodeType(str, Enum):
    ENTITY = "ENTITY"
    DOCUMENT = "DOCUMENT"
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    PROJECT = "PROJECT"
    DATASET = "DATASET"
    MODEL = "MODEL"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    DECISION = "DECISION"
    EVENT = "EVENT"
    POLICY = "POLICY"
    RESOURCE = "RESOURCE"


class KnowledgeRelationship(str, Enum):
    RELATED_TO = "RELATED_TO"
    DEPENDS_ON = "DEPENDS_ON"
    OWNED_BY = "OWNED_BY"
    CREATED_BY = "CREATED_BY"
    MODIFIED_BY = "MODIFIED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    CONTRADICTS = "CONTRADICTS"
    SUPPORTS = "SUPPORTS"
    REFERENCES = "REFERENCES"
    EXECUTES = "EXECUTES"
    USES = "USES"
    GOVERNS = "GOVERNS"
    PRODUCES = "PRODUCES"
    CONSUMES = "CONSUMES"


class KnowledgeNode(BaseModel):
    node_id: str = Field(default_factory=lambda: f"knode_{uuid.uuid4().hex[:10]}")
    label: str
    node_type: KnowledgeNodeType = KnowledgeNodeType.ENTITY
    tenant_id: str = "global"
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


class KnowledgeEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: f"kedge_{uuid.uuid4().hex[:10]}")
    source_node_id: str
    target_node_id: str
    relationship: KnowledgeRelationship = KnowledgeRelationship.RELATED_TO
    tenant_id: str = "global"
    weight: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


class KnowledgeGraphManager:
    """Manages knowledge graph nodes, edges, multi-hop graph traversals, and tenant isolation."""

    def __init__(self) -> None:
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._edges: Dict[str, KnowledgeEdge] = {}

    def add_node(
        self,
        label: str,
        node_type: KnowledgeNodeType = KnowledgeNodeType.ENTITY,
        tenant_id: str = "global",
        properties: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeNode:
        node = KnowledgeNode(label=label, node_type=node_type, tenant_id=tenant_id, properties=properties or {})
        self._nodes[node.node_id] = node
        logger.info(f"[KNOWLEDGE GRAPH] Added node '{node.node_id}' ('{label}', {node_type.value}) for tenant '{tenant_id}'")
        return node

    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship: KnowledgeRelationship = KnowledgeRelationship.RELATED_TO,
        tenant_id: str = "global",
        weight: float = 1.0,
    ) -> KnowledgeEdge:
        if source_node_id not in self._nodes or target_node_id not in self._nodes:
            raise KnowledgeGraphException("Source or target node not found in graph")

        edge = KnowledgeEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship=relationship,
            tenant_id=tenant_id,
            weight=weight,
        )
        self._edges[edge.edge_id] = edge
        logger.info(f"[KNOWLEDGE GRAPH] Added edge '{edge.edge_id}': {source_node_id} -[{relationship.value}]-> {target_node_id}")
        return edge

    def multi_hop_traversal(self, start_node_id: str, max_hops: int = 2, tenant_id: str = "global") -> List[KnowledgeNode]:
        if start_node_id not in self._nodes:
            raise KnowledgeGraphException(f"Start node '{start_node_id}' not found")

        visited = {start_node_id}
        current_layer = [start_node_id]

        for _ in range(max_hops):
            next_layer = []
            for n_id in current_layer:
                for edge in self._edges.values():
                    if edge.tenant_id != tenant_id:
                        continue
                    if edge.source_node_id == n_id and edge.target_node_id not in visited:
                        visited.add(edge.target_node_id)
                        next_layer.append(edge.target_node_id)
                    elif edge.target_node_id == n_id and edge.source_node_id not in visited:
                        visited.add(edge.source_node_id)
                        next_layer.append(edge.source_node_id)
            current_layer = next_layer

        return [self._nodes[n_id] for n_id in visited if self._nodes[n_id].tenant_id == tenant_id]
