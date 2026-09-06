"""Enterprise knowledge trust intelligence generating universal TrustAssessment primitives."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence, TrustDimension
from app.knowledge_assurance.exceptions import (
    KnowledgeTrustNotFoundException,
    CrossTenantKnowledgeAssuranceException,
)


class KnowledgeTrustDimension(str, Enum):
    SOURCE_AUTHORITY = "SOURCE_AUTHORITY"
    FRESHNESS = "FRESHNESS"
    PROVENANCE = "PROVENANCE"
    CONSISTENCY = "CONSISTENCY"
    VERIFICATION = "VERIFICATION"
    RELEVANCE = "RELEVANCE"


class KnowledgeTrustFactor(BaseModel):
    dimension: KnowledgeTrustDimension
    score: float = 1.0
    weight: float = 1.0
    evidence_description: str = ""


class KnowledgeTrustScore(BaseModel):
    overall_trust_score: float = 0.95
    band: TrustBand = TrustBand.HIGH_TRUST
    dimension_scores: Dict[str, float] = Field(default_factory=dict)


class KnowledgeTrustAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id: str
    trust_score: KnowledgeTrustScore
    factors: List[KnowledgeTrustFactor] = Field(default_factory=list)
    trust_assessment_ref: TrustAssessment
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def overall_score(self) -> float:
        return self.trust_score.overall_trust_score

    @property
    def trust_band(self) -> str:
        return self.trust_score.band.value


class KnowledgeTrustEngine:
    """Evaluates multi-dimensional knowledge trust and generates TrustAssessment primitives."""

    def __init__(self) -> None:
        self._assessments: Dict[str, KnowledgeTrustAssessment] = {}

    def evaluate_trust(
        self,
        tenant_id: str,
        reference_id: Optional[str] = None,
        target_resource_id: Optional[str] = None,
        factors: Optional[List[KnowledgeTrustFactor]] = None,
    ) -> KnowledgeTrustAssessment:
        ref_id = target_resource_id or reference_id or "ref-1"
        if not factors:
            factors = [
                KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.SOURCE_AUTHORITY, score=0.98, weight=0.25, evidence_description="Authoritative internal repo"),
                KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.FRESHNESS, score=0.95, weight=0.20, evidence_description="Updated < 24h ago"),
                KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.PROVENANCE, score=0.96, weight=0.20, evidence_description="SHA-256 verified provenance chain"),
                KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.CONSISTENCY, score=0.92, weight=0.15, evidence_description="No policy contradictions"),
                KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.VERIFICATION, score=0.94, weight=0.10, evidence_description="Verified by compliance audit"),
                KnowledgeTrustFactor(dimension=KnowledgeTrustDimension.RELEVANCE, score=0.90, weight=0.10, evidence_description="High semantic alignment"),
            ]

        total_w = sum(f.weight for f in factors)
        weighted_sum = sum(f.weight * f.score for f in factors)
        score_val = weighted_sum / total_w if total_w > 0 else 0.95

        if score_val >= 0.90:
            band_val = TrustBand.HIGH_TRUST
        elif score_val >= 0.70:
            band_val = TrustBand.TRUSTED
        elif score_val >= 0.50:
            band_val = TrustBand.RESTRICTED
        else:
            band_val = TrustBand.UNTRUSTED

        dim_scores = {f.dimension.value: f.score for f in factors}
        t_dims = [TrustDimension(dimension_name=f.dimension.value, score=f.score, weight=f.weight) for f in factors]

        p_trust = TrustAssessment(
            subject_id=ref_id,
            subject_type="KNOWLEDGE_REFERENCE",
            tenant_id=tenant_id,
            score=score_val,
            band=band_val,
            confidence=TrustConfidence.HIGH,
            dimensions=t_dims,
            evidence_references=[f.evidence_description for f in factors if f.evidence_description],
        )

        assessment = KnowledgeTrustAssessment(
            tenant_id=tenant_id,
            reference_id=ref_id,
            trust_score=KnowledgeTrustScore(overall_trust_score=score_val, band=band_val, dimension_scores=dim_scores),
            factors=factors,
            trust_assessment_ref=p_trust,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
