"""
Cross-Domain Trust Assessment Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Evaluates composite cross-domain trust scores for entities, tenants, systems, and models
with tenant isolation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.exceptions import InvalidUnifiedIntelligenceInputException


class UnifiedTrustAssessment:
    """
    Result of a cross-domain trust assessment.
    """

    def __init__(
        self,
        assessment_id: str,
        tenant_id: str,
        entity_reference: str,
        overall_trust_score: float,
        domain_trust_scores: Dict[str, float],
        trust_level: str,  # TRUSTED, VERIFIED, CONDITIONAL, HIGH_RISK, UNTRUSTED
        trust_factors: List[str],
        confidence_score: float,
        created_at: Optional[datetime] = None,
    ):
        self.assessment_id = assessment_id
        self.tenant_id = tenant_id
        self.entity_reference = entity_reference
        self.overall_trust_score = min(max(overall_trust_score, 0.0), 1.0)
        self.domain_trust_scores = domain_trust_scores
        self.trust_level = trust_level
        self.trust_factors = trust_factors
        self.confidence_score = min(max(confidence_score, 0.0), 1.0)
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "tenant_id": self.tenant_id,
            "entity_reference": self.entity_reference,
            "overall_trust_score": round(self.overall_trust_score, 4),
            "domain_trust_scores": {k: round(v, 4) for k, v in self.domain_trust_scores.items()},
            "trust_level": self.trust_level,
            "trust_factors": self.trust_factors,
            "confidence_score": round(self.confidence_score, 4),
            "created_at": self.created_at.isoformat(),
        }


class CrossDomainTrustEngine:
    """
    Computes cross-domain trust scores by combining signals across identity, security, operations, and policy.
    """

    def __init__(self):
        pass

    def evaluate_entity_trust(
        self, tenant_id: str, entity_reference: str, domain_trust_inputs: Dict[str, float]
    ) -> UnifiedTrustAssessment:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if not entity_reference:
            raise InvalidUnifiedIntelligenceInputException("entity_reference is required")

        if not domain_trust_inputs:
            domain_trust_inputs = {
                IntelligenceDomain.IDENTITY.value: 0.9,
                IntelligenceDomain.SECURITY.value: 0.85,
                IntelligenceDomain.OPERATIONS.value: 0.95,
                IntelligenceDomain.POLICY.value: 0.9,
            }

        total_score = sum(domain_trust_inputs.values())
        overall_score = total_score / len(domain_trust_inputs)

        if overall_score >= 0.90:
            level = "TRUSTED"
        elif overall_score >= 0.75:
            level = "VERIFIED"
        elif overall_score >= 0.50:
            level = "CONDITIONAL"
        elif overall_score >= 0.25:
            level = "HIGH_RISK"
        else:
            level = "UNTRUSTED"

        factors = [f"{d} trust score: {score:.2f}" for d, score in domain_trust_inputs.items()]

        assessment_id = f"trust-{uuid.uuid4().hex[:12]}"

        return UnifiedTrustAssessment(
            assessment_id=assessment_id,
            tenant_id=tenant_id,
            entity_reference=entity_reference,
            overall_trust_score=overall_score,
            domain_trust_scores=domain_trust_inputs,
            trust_level=level,
            trust_factors=factors,
            confidence_score=0.88,
        )
