"""
Decision Confidence Scoring Subsystem.
Computes deterministic confidence metrics based on evidence completeness, signal alignment, and model certainty.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field


class DecisionConfidenceScore(BaseModel):
    confidence_id: str = Field(default_factory=lambda: f"conf_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    overall_confidence: float = Field(0.9, ge=0.0, le=1.0)
    evidence_completeness: float = Field(0.95, ge=0.0, le=1.0)
    signal_coherence: float = Field(0.9, ge=0.0, le=1.0)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionConfidenceCalculator:
    """Calculates decision confidence scores."""

    def __init__(self) -> None:
        self._scores: Dict[str, DecisionConfidenceScore] = {}

    def calculate_confidence(
        self,
        decision_id: str,
        tenant_id: str,
        evidence_quality: float = 90.0,
        signal_count: int = 5,
        uncertainty_score: float = 0.1,
    ) -> DecisionConfidenceScore:
        ev_comp = min(1.0, max(0.0, evidence_quality / 100.0))
        sig_coh = min(1.0, max(0.0, 1.0 - uncertainty_score))
        overall = round((ev_comp * 0.5) + (sig_coh * 0.5), 4)

        score = DecisionConfidenceScore(
            decision_id=decision_id,
            tenant_id=tenant_id,
            overall_confidence=overall,
            evidence_completeness=ev_comp,
            signal_coherence=sig_coh,
        )
        self._scores[decision_id] = score
        return score

    def get_confidence(self, decision_id: str) -> Optional[DecisionConfidenceScore]:
        return self._scores.get(decision_id)
