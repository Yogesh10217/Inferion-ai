"""
Cross-Domain Assurance Coordinator Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Coordinated multi-domain assurance evaluation combining domain assurance assessments
into a unified enterprise assurance posture with tenant isolation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException
)
from app.unified_intelligence.domains import IntelligenceDomain


class UnifiedAssurancePosture:
    """
    Unified multi-domain assurance posture representation.
    """
    def __init__(
        self,
        posture_id: str,
        tenant_id: str,
        overall_assurance_score: float,
        domain_assurance_scores: Dict[str, float],
        assurance_level: str,  # HIGH, MODERATE, LOW, DEGRADED
        unmet_assurance_conditions: List[str],
        confidence_score: float,
        created_at: Optional[datetime] = None
    ):
        self.posture_id = posture_id
        self.tenant_id = tenant_id
        self.overall_assurance_score = min(max(overall_assurance_score, 0.0), 1.0)
        self.domain_assurance_scores = domain_assurance_scores
        self.assurance_level = assurance_level
        self.unmet_assurance_conditions = unmet_assurance_conditions
        self.confidence_score = min(max(confidence_score, 0.0), 1.0)
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "posture_id": self.posture_id,
            "tenant_id": self.tenant_id,
            "overall_assurance_score": round(self.overall_assurance_score, 4),
            "domain_assurance_scores": {k: round(v, 4) for k, v in self.domain_assurance_scores.items()},
            "assurance_level": self.assurance_level,
            "unmet_assurance_conditions": self.unmet_assurance_conditions,
            "confidence_score": round(self.confidence_score, 4),
            "created_at": self.created_at.isoformat()
        }


class CrossDomainAssuranceCoordinator:
    """
    Coordinates and synthesizes assurance postures across domain intelligence providers.
    """
    def __init__(self):
        pass

    def evaluate_assurance_posture(
        self,
        tenant_id: str,
        domain_assurance_map: Dict[str, float]
    ) -> UnifiedAssurancePosture:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        if not domain_assurance_map:
            domain_assurance_map = {d.value: 0.85 for d in IntelligenceDomain}

        total_score = sum(domain_assurance_map.values())
        overall_score = total_score / len(domain_assurance_map)

        unmet = []
        for domain, score in domain_assurance_map.items():
            if score < 0.7:
                unmet.append(f"Domain {domain} assurance score ({score:.2f}) below threshold 0.70")

        if overall_score >= 0.85 and not unmet:
            level = "HIGH"
        elif overall_score >= 0.70:
            level = "MODERATE"
        elif overall_score >= 0.50:
            level = "LOW"
        else:
            level = "DEGRADED"

        posture_id = f"assr-{uuid.uuid4().hex[:12]}"
        confidence = 0.90 if len(domain_assurance_map) >= 4 else 0.75

        return UnifiedAssurancePosture(
            posture_id=posture_id,
            tenant_id=tenant_id,
            overall_assurance_score=overall_score,
            domain_assurance_scores=domain_assurance_map,
            assurance_level=level,
            unmet_assurance_conditions=unmet,
            confidence_score=confidence
        )
