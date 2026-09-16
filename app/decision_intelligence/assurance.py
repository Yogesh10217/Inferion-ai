"""
Decision Assurance Subsystem.
Computes overall continuous assurance metrics and compliance ratings for decision workflows.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field


class DecisionAssuranceRating(BaseModel):
    assurance_id: str = Field(default_factory=lambda: f"assur_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    assurance_score: float = Field(92.5, ge=0.0, le=100.0)
    rating: str = "HIGH_ASSURANCE"
    compliance_status: str = "COMPLIANT"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionAssuranceEngine:
    """Evaluates continuous decision assurance."""

    def __init__(self) -> None:
        self._ratings: Dict[str, DecisionAssuranceRating] = {}

    def evaluate_assurance(self, decision_id: str, tenant_id: str, confidence_score: float = 0.9, uncertainty_score: float = 0.1) -> DecisionAssuranceRating:
        score = round(((confidence_score * 0.7) + ((1.0 - uncertainty_score) * 0.3)) * 100.0, 2)
        rating_str = "HIGH_ASSURANCE" if score >= 80.0 else ("MEDIUM_ASSURANCE" if score >= 60.0 else "LOW_ASSURANCE")

        rating = DecisionAssuranceRating(
            decision_id=decision_id,
            tenant_id=tenant_id,
            assurance_score=score,
            rating=rating_str,
        )
        self._ratings[decision_id] = rating
        return rating

    def get_assurance(self, decision_id: str) -> Optional[DecisionAssuranceRating]:
        return self._ratings.get(decision_id)
