"""Cross-Domain Risk Propagation Engine for Phase 5.51 Enterprise AI Unified Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from app.unified_intelligence.domains import IntelligenceDomain


class RiskPropagationNode(BaseModel):
    domain: str
    initial_risk_score: float = 0.0
    current_risk_score: float = 0.0


class RiskPropagationGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"risk-graph-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    nodes: Dict[str, RiskPropagationNode] = Field(default_factory=dict)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class RiskPropagationPath(BaseModel):
    path_id: str = Field(default_factory=lambda: f"risk-path-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    source_domain: IntelligenceDomain
    impacted_domains: List[IntelligenceDomain]
    initial_risk_score: float
    propagated_risk_score: float
    amplification_factor: float = 1.2
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RiskPropagationEngine:
    """Analyzes risk propagation pathways across enterprise domains."""

    def build_graph(
        self, tenant_id: str, edges_data: Optional[List[Tuple[IntelligenceDomain, IntelligenceDomain, float]]] = None
    ) -> RiskPropagationGraph:
        graph = RiskPropagationGraph(tenant_id=tenant_id)
        if edges_data:
            for src, tgt, weight in edges_data:
                src_val = src.value if hasattr(src, "value") else str(src)
                tgt_val = tgt.value if hasattr(tgt, "value") else str(tgt)
                if src_val not in graph.nodes:
                    graph.nodes[src_val] = RiskPropagationNode(domain=src_val)
                if tgt_val not in graph.nodes:
                    graph.nodes[tgt_val] = RiskPropagationNode(domain=tgt_val)
                graph.edges.append({"source": src_val, "target": tgt_val, "weight": weight})
        return graph

    def propagate_risk(
        self, tenant_id: str, graph: RiskPropagationGraph, source_domain: IntelligenceDomain, initial_risk: float = 0.8
    ) -> RiskPropagationGraph:
        src_val = source_domain.value if hasattr(source_domain, "value") else str(source_domain)
        if src_val in graph.nodes:
            graph.nodes[src_val].initial_risk_score = initial_risk
            graph.nodes[src_val].current_risk_score = initial_risk

        # Propagate along edges
        for edge in graph.edges:
            src = edge["source"]
            tgt = edge["target"]
            w = edge["weight"]
            if src in graph.nodes and tgt in graph.nodes:
                propagated = graph.nodes[src].current_risk_score * w
                graph.nodes[tgt].current_risk_score = max(graph.nodes[tgt].current_risk_score, propagated)

        return graph

    def evaluate_risk_propagation(
        self,
        tenant_id: str,
        source_domain: IntelligenceDomain = IntelligenceDomain.IDENTITY,
        initial_risk: float = 40.0,
        impacted_domains: Optional[List[IntelligenceDomain]] = None,
    ) -> RiskPropagationPath:
        impacted = impacted_domains or [
            IntelligenceDomain.SECURITY,
            IntelligenceDomain.DATA,
            IntelligenceDomain.OPERATIONS,
        ]
        amplification = 1.0 + (len(impacted) * 0.1)
        propagated = min(100.0, round(initial_risk * amplification, 2))

        return RiskPropagationPath(
            tenant_id=tenant_id,
            source_domain=source_domain,
            impacted_domains=impacted,
            initial_risk_score=initial_risk,
            propagated_risk_score=propagated,
            amplification_factor=amplification,
        )
