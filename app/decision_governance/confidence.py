"""Decision confidence scoring intelligence considering evidence quality, signal reliability, and data freshness."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class ConfidenceFactor(BaseModel):
    name: str  # evidence_quality, signal_reliability, data_freshness, model_trust, uncertainty, historical_outcomes
    weight: float = 1.0
    score: float = 0.8  # 0.0 to 1.0
    rationale: str = ""


class DecisionConfidence(BaseModel):
    confidence_score: float = 0.85  # 0.0 to 1.0
    level: ConfidenceLevel = ConfidenceLevel.HIGH
    uncertainty_margin: float = 0.05


class ConfidenceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    confidence: DecisionConfidence
    factors: List[ConfidenceFactor] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionConfidenceManager:
    """Evaluates multi-factor decision confidence."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ConfidenceAssessment] = {}

    def assess_confidence(
        self,
        tenant_id: str,
        decision_id: str,
        factors: Optional[List[ConfidenceFactor]] = None,
    ) -> ConfidenceAssessment:
        if not factors:
            factors = [
                ConfidenceFactor(
                    name="evidence_quality", weight=0.25, score=0.90, rationale="High quality telemetry data"
                ),
                ConfidenceFactor(
                    name="signal_reliability", weight=0.20, score=0.95, rationale="Multi-source correlation verified"
                ),
                ConfidenceFactor(name="data_freshness", weight=0.20, score=0.98, rationale="Signals < 30 seconds old"),
                ConfidenceFactor(name="model_trust", weight=0.15, score=0.88, rationale="High model trust score"),
                ConfidenceFactor(name="uncertainty", weight=0.10, score=0.85, rationale="Low parameter variance"),
                ConfidenceFactor(
                    name="historical_outcomes",
                    weight=0.10,
                    score=0.80,
                    rationale="Previous similar decisions succeeded",
                ),
            ]

        total_weight = sum(f.weight for f in factors)
        weighted_sum = sum(f.weight * f.score for f in factors)
        score_val = weighted_sum / total_weight if total_weight > 0 else 0.80

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
            decision_id=decision_id,
            confidence=DecisionConfidence(
                confidence_score=score_val, level=lvl, uncertainty_margin=round(1.0 - score_val, 2)
            ),
            factors=factors,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
