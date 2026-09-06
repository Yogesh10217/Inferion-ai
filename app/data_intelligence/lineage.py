"""Enterprise data lineage intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import DataLineageNotFoundException, CrossTenantDataIntelligenceException


class LineageType(str, Enum):
    SOURCE_TO_DATASET = "SOURCE_TO_DATASET"
    DATASET_TO_PIPELINE = "DATASET_TO_PIPELINE"
    PIPELINE_TO_TRANSFORMATION = "PIPELINE_TO_TRANSFORMATION"
    TRANSFORMATION_TO_DATASET = "TRANSFORMATION_TO_DATASET"
    DATASET_TO_MODEL = "DATASET_TO_MODEL"
    MODEL_TO_AGENT = "MODEL_TO_AGENT"
    AGENT_TO_KNOWLEDGE = "AGENT_TO_KNOWLEDGE"
    KNOWLEDGE_TO_DECISION = "KNOWLEDGE_TO_DECISION"


class LineageNode(BaseModel):
    node_id: str
    name: str
    node_type: str  # SOURCE, DATASET, PIPELINE, TRANSFORMATION, MODEL, AGENT, KNOWLEDGE, DECISION
    tenant_id: str
    asset_reference_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LineageRelationship(BaseModel):
    relationship_id: str
    source_node_id: str
    target_node_id: str
    lineage_type: LineageType
    tenant_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LineageEvidence(BaseModel):
    evidence_id: str
    lineage_id: str
    tenant_id: str
    provenance_hash: str
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataLineage(BaseModel):
    lineage_id: str
    tenant_id: str
    nodes: List[LineageNode] = Field(default_factory=list)
    relationships: List[LineageRelationship] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataLineageManager:
    """Manages lineage references across platform entities."""

    def __init__(self) -> None:
        self._nodes: Dict[str, LineageNode] = {}
        self._relationships: Dict[str, LineageRelationship] = {}
        self._lineages: Dict[str, DataLineage] = {}

    def register_node(
        self,
        name: str,
        node_type: str,
        tenant_id: str,
        asset_reference_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        node_id: Optional[str] = None,
    ) -> LineageNode:
        nid = node_id or f"lnode-{uuid.uuid4().hex[:8]}"
        node = LineageNode(
            node_id=nid,
            name=name,
            node_type=node_type,
            tenant_id=tenant_id,
            asset_reference_id=asset_reference_id,
            metadata=metadata or {},
        )
        self._nodes[nid] = node
        return node

    def add_relationship(
        self,
        source_node_id: str,
        target_node_id: str,
        lineage_type: LineageType,
        tenant_id: str,
        relationship_id: Optional[str] = None,
    ) -> LineageRelationship:
        s_node = self._nodes.get(source_node_id)
        t_node = self._nodes.get(target_node_id)
        if (s_node and s_node.tenant_id != tenant_id) or (t_node and t_node.tenant_id != tenant_id):
            raise CrossTenantDataIntelligenceException()

        rid = relationship_id or f"lrel-{uuid.uuid4().hex[:8]}"
        rel = LineageRelationship(
            relationship_id=rid,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            lineage_type=lineage_type,
            tenant_id=tenant_id,
        )
        self._relationships[rid] = rel
        return rel

    def get_lineage(self, tenant_id: str, root_node_id: Optional[str] = None) -> DataLineage:
        nodes = [n for n in self._nodes.values() if n.tenant_id == tenant_id]
        rels = [r for r in self._relationships.values() if r.tenant_id == tenant_id]

        lid = f"lineage-{uuid.uuid4().hex[:8]}"
        dl = DataLineage(
            lineage_id=lid,
            tenant_id=tenant_id,
            nodes=nodes,
            relationships=rels,
        )
        self._lineages[lid] = dl
        return dl
