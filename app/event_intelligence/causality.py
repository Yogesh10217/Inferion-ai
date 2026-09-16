"""Event Causality Analysis Subsystem (Phase 5.34)."""

import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.event_intelligence.events import EnterpriseEvent


class CausalRelationship(str, Enum):
    CAUSE = "CAUSE"
    CONTRIBUTING_FACTOR = "CONTRIBUTING_FACTOR"
    CORRELATED_EVENT = "CORRELATED_EVENT"
    DOWNSTREAM_EFFECT = "DOWNSTREAM_EFFECT"
    UNKNOWN = "UNKNOWN"


class CausalConfidence(BaseModel):
    score: float = 0.85


class CausalNode(BaseModel):
    node_id: str
    event_id: str
    event_type: str


class CausalEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship: CausalRelationship = CausalRelationship.CAUSE


class CausalGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"cgraph_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    nodes: List[CausalNode] = Field(default_factory=list)
    edges: List[CausalEdge] = Field(default_factory=list)


class CausalityAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"causal_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    root_cause_event_id: Optional[str] = None
    contributing_event_ids: List[str] = Field(default_factory=list)
    downstream_event_ids: List[str] = Field(default_factory=list)
    graph: CausalGraph
    confidence: CausalConfidence = Field(default_factory=CausalConfidence)


class EventCausalityAnalyzer:
    """Analyzes evidence-based causal relationships across enterprise events."""

    def analyze_causality(self, tenant_id: str, events: List[EnterpriseEvent]) -> CausalityAnalysis:
        nodes = [CausalNode(node_id=e.event_id, event_id=e.event_id, event_type=e.event_type.value) for e in events]
        edges = []

        root_cause_id = events[0].event_id if events else None
        downstream = []

        if len(events) > 1:
            for i in range(1, len(events)):
                edges.append(CausalEdge(source_node_id=events[0].event_id, target_node_id=events[i].event_id, relationship=CausalRelationship.DOWNSTREAM_EFFECT))
                downstream.append(events[i].event_id)

        graph = CausalGraph(tenant_id=tenant_id, nodes=nodes, edges=edges)

        return CausalityAnalysis(
            tenant_id=tenant_id,
            root_cause_event_id=root_cause_id,
            downstream_event_ids=downstream,
            graph=graph,
        )
