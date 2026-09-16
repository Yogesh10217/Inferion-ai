"""Data Lineage Manager & Lineage Graph Engine."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class LineageNode(BaseModel):
    """Node in data lineage graph."""

    node_id: str
    node_type: str  # DATA_SOURCE, CONNECTOR, INGESTION, NORMALIZATION, TRANSFORMATION, KNOWLEDGE_INDEX, AGENT, WORKFLOW, EXECUTION
    name: str
    tenant_id: str = "global"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LineageEdge(BaseModel):
    """Directed edge in data lineage graph."""

    edge_id: str = Field(default_factory=lambda: f"edge_{uuid.uuid4().hex[:10]}")
    source_node_id: str
    target_node_id: str
    relationship_type: str = "TRANSFORMS_TO"
    created_at: datetime = Field(default_factory=_now)


class LineageEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"lineage_evt_{uuid.uuid4().hex[:10]}")
    source_node_id: str
    target_node_id: str
    tenant_id: str = "global"
    recorded_at: datetime = Field(default_factory=_now)


class DataLineageManager:
    """Manages end-to-end data lineage tracing from raw source to AI execution."""

    def __init__(self) -> None:
        self._nodes: Dict[str, LineageNode] = {}
        self._edges: List[LineageEdge] = []

    def record_node(self, node_id: str, node_type: str, name: str, tenant_id: str = "global", metadata: Optional[Dict[str, Any]] = None) -> LineageNode:
        node = LineageNode(
            node_id=node_id,
            node_type=node_type,
            name=name,
            tenant_id=tenant_id,
            metadata=metadata or {},
        )
        self._nodes[node_id] = node
        return node

    def record_lineage(self, source_node_id: str, target_node_id: str, relationship_type: str = "PRODUCES") -> LineageEdge:
        if source_node_id not in self._nodes:
            self.record_node(source_node_id, "UNKNOWN", source_node_id)
        if target_node_id not in self._nodes:
            self.record_node(target_node_id, "UNKNOWN", target_node_id)

        edge = LineageEdge(source_node_id=source_node_id, target_node_id=target_node_id, relationship_type=relationship_type)
        self._edges.append(edge)
        logger.info(f"[DATA LINEAGE] Lineage link: '{source_node_id}' --({relationship_type})--> '{target_node_id}'")
        return edge

    def get_upstream_lineage(self, node_id: str) -> List[LineageNode]:
        upstream_ids = [e.source_node_id for e in self._edges if e.target_node_id == node_id]
        return [self._nodes[nid] for nid in upstream_ids if nid in self._nodes]

    def get_downstream_lineage(self, node_id: str) -> List[LineageNode]:
        downstream_ids = [e.target_node_id for e in self._edges if e.source_node_id == node_id]
        return [self._nodes[nid] for nid in downstream_ids if nid in self._nodes]
