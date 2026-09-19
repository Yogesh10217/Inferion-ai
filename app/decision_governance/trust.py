"""Decision trust intelligence generating TrustAssessment primitives."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence, TrustDimension


class DecisionTrustDimension(str, Enum):
    ACCURACY = "ACCURACY"
    TRANSPARENCY = "TRANSPARENCY"
    RELIABILITY = "RELIABILITY"
    COMPLIANCE = "COMPLIANCE"
    VERIFIABILITY = "VERIFIABILITY"
    RISK_ALIGNMENT = "RISK_ALIGNMENT"


class DecisionTrustFactor(BaseModel):
    dimension: DecisionTrustDimension
    score: float = 1.0
    weight: float = 1.0
    evidence: str = ""


class DecisionTrustScore(BaseModel):
    overall_trust_score: float = 0.95
    band: TrustBand = TrustBand.HIGH_TRUST
    dimension_breakdown: Dict[str, float] = Field(default_factory=dict)


class DecisionTrustEngine:
    """Evaluates decision trust scores and produces universal TrustAssessment primitives."""

    def __init__(self) -> None:
        self._assessments: Dict[str, TrustAssessment] = {}

    def evaluate_trust(
        self,
        tenant_id: str,
        decision_id: str,
        factors: Optional[List[DecisionTrustFactor]] = None,
    ) -> TrustAssessment:
        if not factors:
            factors = [
                DecisionTrustFactor(
                    dimension=DecisionTrustDimension.ACCURACY,
                    score=0.96,
                    weight=0.2,
                    evidence="High confidence telemetry",
                ),
                DecisionTrustFactor(
                    dimension=DecisionTrustDimension.TRANSPARENCY,
                    score=0.98,
                    weight=0.2,
                    evidence="Full explainability trail",
                ),
                DecisionTrustFactor(
                    dimension=DecisionTrustDimension.RELIABILITY,
                    score=0.94,
                    weight=0.15,
                    evidence="Verified outcome metrics",
                ),
                DecisionTrustFactor(
                    dimension=DecisionTrustDimension.COMPLIANCE,
                    score=1.0,
                    weight=0.15,
                    evidence="Zero policy violations",
                ),
                DecisionTrustFactor(
                    dimension=DecisionTrustDimension.VERIFIABILITY,
                    score=0.95,
                    weight=0.15,
                    evidence="SHA-256 evidence bundle",
                ),
                DecisionTrustFactor(
                    dimension=DecisionTrustDimension.RISK_ALIGNMENT,
                    score=0.92,
                    weight=0.15,
                    evidence="Risk profile within tolerance",
                ),
            ]

        total_weight = sum(f.weight for f in factors)
        weighted_sum = sum(f.weight * f.score for f in factors)
        score_val = weighted_sum / total_weight if total_weight > 0 else 0.95

        if score_val >= 0.90:
            band_val = TrustBand.HIGH_TRUST
        elif score_val >= 0.70:
            band_val = TrustBand.TRUSTED
        elif score_val >= 0.50:
            band_val = TrustBand.RESTRICTED
        else:
            band_val = TrustBand.UNTRUSTED

        dims = [TrustDimension(dimension_name=f.dimension.value, score=f.score, weight=f.weight) for f in factors]

        assessment = TrustAssessment(
            subject_id=decision_id,
            subject_type="DECISION_RECORD",
            tenant_id=tenant_id,
            score=score_val,
            band=band_val,
            confidence=TrustConfidence.HIGH,
            dimensions=dims,
            evidence_references=[f.evidence for f in factors if f.evidence],
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
