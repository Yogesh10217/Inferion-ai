"""Knowledge confidence intelligence considering reliability, freshness, and evidence quality."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class ConfidenceFactor(BaseModel):
    name: str  # source_reliability, provenance, freshness, evidence, consistency, historical_verification
    weight: float = 1.0
    score: float = 0.85
    rationale: str = ""


class KnowledgeConfidence(BaseModel):
    confidence_score: float = 0.88
    level: ConfidenceLevel = ConfidenceLevel.HIGH
    uncertainty_margin: float = 0.05


class ConfidenceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id: str
    confidence: KnowledgeConfidence
    factors: List[ConfidenceFactor] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def overall_confidence(self) -> float:
        return self.confidence.confidence_score

    @property
    def confidence_level(self) -> str:
        return self.confidence.level.value


class KnowledgeConfidenceManager:
    """Evaluates multi-factor confidence for knowledge assets."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ConfidenceAssessment] = {}

    def evaluate_confidence(
        self,
        tenant_id: str,
        reference_id: Optional[str] = None,
        target_resource_id: Optional[str] = None,
        factors: Optional[List[ConfidenceFactor]] = None,
    ) -> ConfidenceAssessment:
        ref_id = target_resource_id or reference_id or "ref-1"
        return self.assess_confidence(tenant_id=tenant_id, reference_id=ref_id, factors=factors)

    def assess_confidence(
        self,
        tenant_id: str,
        reference_id: str,
        factors: Optional[List[ConfidenceFactor]] = None,
    ) -> ConfidenceAssessment:
        if not factors:
            factors = [
                ConfidenceFactor(name="source_reliability", weight=0.25, score=0.92, rationale="High authority source"),
                ConfidenceFactor(name="provenance", weight=0.20, score=0.95, rationale="Complete origin chain"),
                ConfidenceFactor(name="freshness", weight=0.20, score=0.98, rationale="Updated within SLA boundary"),
                ConfidenceFactor(
                    name="evidence", weight=0.15, score=0.90, rationale="Multiple supporting evidence references"
                ),
                ConfidenceFactor(name="consistency", weight=0.10, score=0.94, rationale="Zero policy conflicts"),
                ConfidenceFactor(
                    name="historical_verification", weight=0.10, score=0.88, rationale="Verified in prior audits"
                ),
            ]

        total_weight = sum(f.weight for f in factors)
        weighted_sum = sum(f.weight * f.score for f in factors)
        score_val = weighted_sum / total_weight if total_weight > 0 else 0.88

        if score_val >= 0.90:
            lvl = ConfidenceLevel.VERY_HIGH
        elif score_val >= 0.75:
            lvl = ConfidenceLevel.HIGH
        elif score_val >= 0.50:
            lvl = ConfidenceLevel.MEDIUM
        else:
            lvl = ConfidenceLevel.LOW

        assessment = ConfidenceAssessment(
            tenant_id=tenant_id,
            reference_id=reference_id,
            confidence=KnowledgeConfidence(
                confidence_score=score_val,
                level=lvl,
                uncertainty_margin=round(1.0 - score_val, 2),
            ),
            factors=factors,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
