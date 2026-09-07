"""Confidence Calculator & Score Engine."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ConfidenceScore(BaseModel):
    score: float  # 0.0 to 1.0
    level: str  # LOW, MEDIUM, HIGH, VERIFIED
    factors: Dict[str, float] = Field(default_factory=dict)


class ConfidenceCalculator:
    """Calculates standardized confidence score across multi-domain signals and hypotheses."""

    @staticmethod
    def calculate_confidence(
        base_confidence: float = 0.8,
        evidence_count: int = 1,
        correlating_domains_count: int = 1,
        trust_score: float = 80.0,
    ) -> ConfidenceScore:
        ev_factor = min(0.2, evidence_count * 0.05)
        domain_factor = min(0.2, (correlating_domains_count - 1) * 0.1)
        trust_factor = (trust_score / 100.0) * 0.1

        final_score = min(1.0, round(base_confidence + ev_factor + domain_factor + trust_factor, 2))

        if final_score >= 0.9:
            level = "VERIFIED"
        elif final_score >= 0.75:
            level = "HIGH"
        elif final_score >= 0.5:
            level = "MEDIUM"
        else:
            level = "LOW"

        return ConfidenceScore(
            score=final_score,
            level=level,
            factors={
                "base": base_confidence,
                "evidence_bonus": ev_factor,
                "domain_bonus": domain_factor,
                "trust_bonus": trust_factor,
            },
        )
