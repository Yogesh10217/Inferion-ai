"""Cross-Asset Lineage Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import CrossTenantLifecycleAccessException


class LineageRelationshipType(str, Enum):
    TRAINED_ON = "TRAINED_ON"
    DERIVED_FROM = "DERIVED_FROM"
    EVALUATED_BY = "EVALUATED_BY"
    DEPENDS_ON = "DEPENDS_ON"
    DEPLOYED_WITH = "DEPLOYED_WITH"
    USES_TOOL = "USES_TOOL"
    USES_KNOWLEDGE = "USES_KNOWLEDGE"
    REPLACED_BY = "REPLACED_BY"
    SUPERSEDES = "SUPERSEDES"


class AssetLineage(BaseModel):
    asset_id: str
    tenant_id: str
    upstream_ids: List[str] = Field(default_factory=list)
    downstream_ids: List[str] = Field(default_factory=list)


class LineageNode(BaseModel):

    node_id: str
    asset_id: str
    asset_name: str
    asset_type: str


class LineageEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: f"ledge_{uuid.uuid4().hex[:12]}")
    source_node_id: str
    target_node_id: str
    relationship: LineageRelationshipType


class LineageGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"lgraph_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    nodes: List[LineageNode] = Field(default_factory=list)
    edges: List[LineageEdge] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LineageManager:
    """Manages tenant-isolated cross-asset lifecycle lineage graphs."""

    def __init__(self) -> None:
        self._graphs: Dict[str, LineageGraph] = {}

    def record_lineage(
        self,
        tenant_id: str,
        source_asset_id: str,
        target_asset_id: str,
        relationship: LineageRelationshipType,
        source_name: str = "SourceAsset",
        target_name: str = "TargetAsset",
    ) -> LineageGraph:
        n1 = LineageNode(node_id=source_asset_id, asset_id=source_asset_id, asset_name=source_name, asset_type="ASSET")
        n2 = LineageNode(node_id=target_asset_id, asset_id=target_asset_id, asset_name=target_name, asset_type="ASSET")
        edge = LineageEdge(source_node_id=source_asset_id, target_node_id=target_asset_id, relationship=relationship)

        graph = LineageGraph(tenant_id=tenant_id, nodes=[n1, n2], edges=[edge])
        self._graphs[graph.graph_id] = graph
        return graph

    def get_graph(self, graph_id: str, tenant_id: str) -> LineageGraph:
        graph = self._graphs.get(graph_id)
        if not graph:
            raise KeyError(f"Lineage graph '{graph_id}' not found.")
        if tenant_id != "global" and graph.tenant_id != "global" and tenant_id != graph.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, graph.tenant_id)
        return graph
