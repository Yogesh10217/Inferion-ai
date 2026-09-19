"""
Unified Risk Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Calculates cross-domain enterprise risk scores, evaluates risk vectors,
and tracks risk trends across domains with tenant isolation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException,
)
from app.unified_intelligence.risk_propagation import RiskPropagationGraph


class UnifiedRiskAssessment:
    """
    Holistic cross-domain risk assessment result.
    """

    def __init__(
        self,
        assessment_id: str,
        tenant_id: str,
        overall_risk_score: float,
        risk_level: str,
        domain_risk_scores: Dict[str, float],
        top_risk_factors: List[str],
        confidence_score: float,
        recommendations_count: int,
        created_at: Optional[datetime] = None,
    ):
        self.assessment_id = assessment_id
        self.tenant_id = tenant_id
        self.overall_risk_score = min(max(overall_risk_score, 0.0), 1.0)
        self.risk_level = risk_level  # LOW, MEDIUM, HIGH, CRITICAL
        self.domain_risk_scores = domain_risk_scores
        self.top_risk_factors = top_risk_factors
        self.confidence_score = min(max(confidence_score, 0.0), 1.0)
        self.recommendations_count = recommendations_count
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "tenant_id": self.tenant_id,
            "overall_risk_score": round(self.overall_risk_score, 4),
            "risk_level": self.risk_level,
            "domain_risk_scores": {k: round(v, 4) for k, v in self.domain_risk_scores.items()},
            "top_risk_factors": self.top_risk_factors,
            "confidence_score": round(self.confidence_score, 4),
            "recommendations_count": self.recommendations_count,
            "created_at": self.created_at.isoformat(),
        }


class UnifiedRiskEngine:
    """
    Evaluates enterprise-wide multi-domain risk scores combining signals, situations, and risk propagation graphs.
    """

    def __init__(self):
        pass

    def evaluate_risk(
        self, tenant_id: str, domain_inputs: List[Any], risk_graph: Optional[RiskPropagationGraph] = None
    ) -> UnifiedRiskAssessment:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        domain_scores: Dict[str, List[float]] = {}
        for domain in IntelligenceDomain:
            domain_scores[domain.value] = []

        total_confidence = 0.0
        count = 0

        for inp in domain_inputs:
            if hasattr(inp, "tenant_id") and inp.tenant_id != tenant_id:
                raise CrossTenantUnifiedIntelligenceException(
                    f"Tenant mismatch in risk evaluation: expected {tenant_id}, got {inp.tenant_id}"
                )
            domain_val = inp.domain.value if hasattr(inp.domain, "value") else str(inp.domain)
            risk = getattr(inp, "risk_score", 0.5)
            conf = getattr(inp, "confidence_score", 0.8)
            domain_scores.setdefault(domain_val, []).append(risk)
            total_confidence += conf
            count += 1

        avg_domain_scores: Dict[str, float] = {}
        for d, scores in domain_scores.items():
            avg_domain_scores[d] = sum(scores) / len(scores) if scores else 0.1

        overall_score = sum(avg_domain_scores.values()) / len(avg_domain_scores)

        # Factor in propagation graph if present
        if risk_graph:
            if risk_graph.tenant_id != tenant_id:
                raise CrossTenantUnifiedIntelligenceException(
                    f"Tenant mismatch in risk graph: expected {tenant_id}, got {risk_graph.tenant_id}"
                )
            graph_max_score = max([node.current_risk_score for node in risk_graph.nodes.values()], default=0.0)
            overall_score = max(overall_score, graph_max_score * 0.9)

        if overall_score >= 0.8:
            risk_level = "CRITICAL"
        elif overall_score >= 0.6:
            risk_level = "HIGH"
        elif overall_score >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        avg_confidence = (total_confidence / count) if count > 0 else 0.85
        assessment_id = f"risk-{uuid.uuid4().hex[:12]}"

        top_factors = [
            f"Cross-domain risk amplification in {d}"
            for d, score in sorted(avg_domain_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            if score > 0.3
        ]

        return UnifiedRiskAssessment(
            assessment_id=assessment_id,
            tenant_id=tenant_id,
            overall_risk_score=overall_score,
            risk_level=risk_level,
            domain_risk_scores=avg_domain_scores,
            top_risk_factors=top_factors,
            confidence_score=avg_confidence,
            recommendations_count=len(top_factors) + 1,
        )
