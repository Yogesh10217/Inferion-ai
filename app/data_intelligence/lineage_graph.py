"""Analytical lineage graph (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import DataLineageNotFoundException, CrossTenantDataIntelligenceException
from app.data_intelligence.lineage import DataLineageManager, LineageNode, LineageRelationship


class TraversalDirection(str, Enum):
    UPSTREAM = "UPSTREAM"
    DOWNSTREAM = "DOWNSTREAM"
    BOTH = "BOTH"


class DataLineageGraphNode(BaseModel):
    node_id: str
    name: str
    node_type: str
    asset_reference_id: str


class DataLineageGraphEdge(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    relationship_type: str


class DataLineageGraph(BaseModel):
    graph_id: str
    tenant_id: str
    nodes: Dict[str, DataLineageGraphNode] = Field(default_factory=dict)
    edges: List[DataLineageGraphEdge] = Field(default_factory=list)


class LineageTraversalResult(BaseModel):
    traversal_id: str
    root_node_id: str
    direction: TraversalDirection
    visited_node_ids: List[str]
    impacted_models: List[str] = Field(default_factory=list)
    impacted_agents: List[str] = Field(default_factory=list)
    impacted_knowledge: List[str] = Field(default_factory=list)
    impacted_decisions: List[str] = Field(default_factory=list)
    blast_radius_score: float = 0.0


class DataLineageGraphManager:
    """Manages analytical traversal and impact analysis on lineage graphs."""

    def __init__(self, lineage_manager: Optional[DataLineageManager] = None) -> None:
        self.lineage_manager = lineage_manager or DataLineageManager()

    def build_graph(self, tenant_id: str) -> DataLineageGraph:
        lineage = self.lineage_manager.get_lineage(tenant_id)
        gid = f"graph-{uuid.uuid4().hex[:8]}"

        nodes_map = {
            n.node_id: DataLineageGraphNode(
                node_id=n.node_id,
                name=n.name,
                node_type=n.node_type,
                asset_reference_id=n.asset_reference_id,
            )
            for n in lineage.nodes
        }

        edges_list = [
            DataLineageGraphEdge(
                edge_id=r.relationship_id,
                source_id=r.source_node_id,
                target_id=r.target_node_id,
                relationship_type=r.lineage_type.value,
            )
            for r in lineage.relationships
        ]

        return DataLineageGraph(
            graph_id=gid,
            tenant_id=tenant_id,
            nodes=nodes_map,
            edges=edges_list,
        )

    def traverse(
        self,
        tenant_id: str,
        start_node_id: str,
        direction: TraversalDirection = TraversalDirection.DOWNSTREAM,
    ) -> LineageTraversalResult:
        graph = self.build_graph(tenant_id)

        if start_node_id not in graph.nodes and graph.nodes:
            # Fallback check for asset_reference_id matching start_node_id
            for n_id, n in graph.nodes.items():
                if n.asset_reference_id == start_node_id:
                    start_node_id = n_id
                    break

        visited: Set[str] = set()
        queue = [start_node_id]

        impacted_models = []
        impacted_agents = []
        impacted_knowledge = []
        impacted_decisions = []

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)

            node = graph.nodes.get(curr)
            if node:
                if node.node_type == "MODEL":
                    impacted_models.append(node.asset_reference_id)
                elif node.node_type == "AGENT":
                    impacted_agents.append(node.asset_reference_id)
                elif node.node_type == "KNOWLEDGE":
                    impacted_knowledge.append(node.asset_reference_id)
                elif node.node_type == "DECISION":
                    impacted_decisions.append(node.asset_reference_id)

            # Find neighbors based on direction
            for edge in graph.edges:
                if direction in (TraversalDirection.DOWNSTREAM, TraversalDirection.BOTH) and edge.source_id == curr:
                    if edge.target_id not in visited:
                        queue.append(edge.target_id)
                if direction in (TraversalDirection.UPSTREAM, TraversalDirection.BOTH) and edge.target_id == curr:
                    if edge.source_id not in visited:
                        queue.append(edge.source_id)

        tid = f"trav-{uuid.uuid4().hex[:8]}"
        blast_score = len(visited) * 1.5

        return LineageTraversalResult(
            traversal_id=tid,
            root_node_id=start_node_id,
            direction=direction,
            visited_node_ids=list(visited),
            impacted_models=impacted_models,
            impacted_agents=impacted_agents,
            impacted_knowledge=impacted_knowledge,
            impacted_decisions=impacted_decisions,
            blast_radius_score=round(blast_score, 2),
        )
