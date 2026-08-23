"""Immutable Data Lineage Tracking Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.data_governance.exceptions import DataLineageException, CrossTenantDataAccessException


class LineageNodeType(str, Enum):
    SOURCE = "SOURCE"
    INGESTION = "INGESTION"
    TRANSFORMATION = "TRANSFORMATION"
    DATASET = "DATASET"
    KNOWLEDGE = "KNOWLEDGE"
    MODEL_AGENT = "MODEL_AGENT"
    WORKFLOW = "WORKFLOW"
    APPLICATION = "APPLICATION"
    OUTPUT = "OUTPUT"


class LineageNode(BaseModel):
    node_id: str
    tenant_id: str
    name: str
    node_type: LineageNodeType
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LineageEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    source_node_id: str
    target_node_id: str
    relationship: str = "DERIVED_FROM"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LineageEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    actor_identity: str
    source: str
    target: str
    operation: str
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataLineage(BaseModel):
    tenant_id: str
    nodes: Dict[str, LineageNode] = Field(default_factory=dict)
    edges: List[LineageEdge] = Field(default_factory=list)
    events: List[LineageEvent] = Field(default_factory=list)


class DataLineageManager:
    """Manages immutable lineage graphs while strictly preventing cross-tenant leakage."""

    def __init__(self) -> None:
        self._lineages: Dict[str, DataLineage] = {}

    def _get_or_create_lineage(self, tenant_id: str) -> DataLineage:
        if tenant_id not in self._lineages:
            self._lineages[tenant_id] = DataLineage(tenant_id=tenant_id)
        return self._lineages[tenant_id]

    def record_lineage_event(
        self,
        tenant_id: str,
        actor_identity: str,
        source_id: str,
        source_name: str,
        source_type: LineageNodeType,
        target_id: str,
        target_name: str,
        target_type: LineageNodeType,
        operation: str,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LineageEvent:
        lineage = self._get_or_create_lineage(tenant_id)

        # Register nodes if not present
        if source_id not in lineage.nodes:
            lineage.nodes[source_id] = LineageNode(
                node_id=source_id,
                tenant_id=tenant_id,
                name=source_name,
                node_type=source_type,
            )
        if target_id not in lineage.nodes:
            lineage.nodes[target_id] = LineageNode(
                node_id=target_id,
                tenant_id=tenant_id,
                name=target_name,
                node_type=target_type,
            )

        # Add edge
        edge = LineageEdge(
            tenant_id=tenant_id,
            source_node_id=source_id,
            target_node_id=target_id,
            relationship=operation,
        )
        lineage.edges.append(edge)

        # Add immutable event log
        event = LineageEvent(
            tenant_id=tenant_id,
            actor_identity=actor_identity,
            source=source_id,
            target=target_id,
            operation=operation,
            correlation_id=correlation_id or str(uuid.uuid4()),
            metadata=metadata or {},
        )
        lineage.events.append(event)
        return event

    def get_asset_lineage(self, asset_id: str, tenant_id: str) -> DataLineage:
        """Retrieve complete lineage for a tenant without leaking metadata from other tenants."""
        if tenant_id not in self._lineages:
            return DataLineage(tenant_id=tenant_id)

        full_lineage = self._lineages[tenant_id]

        relevant_nodes = set()
        if asset_id in full_lineage.nodes or any(e.source_node_id == asset_id or e.target_node_id == asset_id for e in full_lineage.edges):
            relevant_nodes.add(asset_id)
            # Breadth-first search for all connected nodes in graph component
            added = True
            while added:
                added = False
                for edge in full_lineage.edges:
                    if edge.source_node_id in relevant_nodes and edge.target_node_id not in relevant_nodes:
                        relevant_nodes.add(edge.target_node_id)
                        added = True
                    elif edge.target_node_id in relevant_nodes and edge.source_node_id not in relevant_nodes:
                        relevant_nodes.add(edge.source_node_id)
                        added = True

        nodes = {nid: n for nid, n in full_lineage.nodes.items() if nid in relevant_nodes}
        edges = [e for e in full_lineage.edges if e.source_node_id in relevant_nodes and e.target_node_id in relevant_nodes]
        events = [ev for ev in full_lineage.events if ev.source in relevant_nodes or ev.target in relevant_nodes]

        return DataLineage(tenant_id=tenant_id, nodes=nodes, edges=edges, events=events)


    def calculate_lineage_completeness(self, asset_id: str, tenant_id: str) -> float:
        """Calculate lineage completeness score (0.0 to 100.0)."""
        lineage = self.get_asset_lineage(asset_id, tenant_id)
        if not lineage.nodes:
            return 20.0  # Or low score if no lineage registered

        node_types = set(n.node_type for n in lineage.nodes.values())
        # Ideal path has SOURCE, INGESTION/TRANSFORMATION, KNOWLEDGE/MODEL
        has_source = LineageNodeType.SOURCE in node_types or LineageNodeType.DATASET in node_types
        has_transform = LineageNodeType.TRANSFORMATION in node_types or LineageNodeType.INGESTION in node_types
        has_consumer = LineageNodeType.KNOWLEDGE in node_types or LineageNodeType.MODEL_AGENT in node_types or LineageNodeType.APPLICATION in node_types

        score = 40.0
        if has_source:
            score += 20.0
        if has_transform:
            score += 20.0
        if has_consumer:
            score += 20.0
        return score
