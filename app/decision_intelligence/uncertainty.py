"""
Decision Uncertainty Assessment Subsystem (Addition #3).
Evaluates decision uncertainty across data, evidence, model, context, conflicting signals, and insufficient evidence dimensions.
Complements confidence scoring by quantifying residual ambiguity.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import (
    CrossTenantDecisionIntelligenceException,
    DecisionNotFoundException,
)


class UncertaintyDimension(str, Enum):
    DATA_UNCERTAINTY = "DATA_UNCERTAINTY"
    EVIDENCE_UNCERTAINTY = "EVIDENCE_UNCERTAINTY"
    MODEL_UNCERTAINTY = "MODEL_UNCERTAINTY"
    CONTEXT_UNCERTAINTY = "CONTEXT_UNCERTAINTY"
    CONFLICTING_SIGNALS = "CONFLICTING_SIGNALS"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class UncertaintyLevel(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DecisionUncertaintyDimensionScore(BaseModel):
    dimension: UncertaintyDimension
    score: float = Field(
        0.0, ge=0.0, le=1.0, description="Uncertainty score between 0.0 (certain) and 1.0 (highly uncertain)"
    )
    reasoning: str = ""


class DecisionUncertaintyAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"uncert_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    overall_uncertainty: float = Field(0.0, ge=0.0, le=1.0)
    level: UncertaintyLevel = UncertaintyLevel.LOW
    dimensions: List[DecisionUncertaintyDimensionScore] = Field(default_factory=list)
    key_drivers: List[str] = Field(default_factory=list)
    mitigation_recommendations: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionUncertaintyEngine:
    """Engine for assessing decision uncertainty across standard platform dimensions."""

    def __init__(self) -> None:
        self._assessments: Dict[str, DecisionUncertaintyAssessment] = {}

    def assess_uncertainty(
        self,
        decision_id: str,
        tenant_id: str,
        dimension_inputs: Optional[Dict[UncertaintyDimension, float]] = None,
        conflicting_signal_count: int = 0,
        evidence_quality_score: float = 1.0,
    ) -> DecisionUncertaintyAssessment:
        dimension_scores: List[DecisionUncertaintyDimensionScore] = []
        inputs = dimension_inputs or {}

        # 1. Data uncertainty
        data_unc = inputs.get(UncertaintyDimension.DATA_UNCERTAINTY, 0.1)
        dimension_scores.append(
            DecisionUncertaintyDimensionScore(
                dimension=UncertaintyDimension.DATA_UNCERTAINTY,
                score=data_unc,
                reasoning="Evaluated based on input telemetry freshness and variance.",
            )
        )

        # 2. Evidence uncertainty
        ev_unc = max(
            0.0,
            min(
                1.0, 1.0 - (evidence_quality_score / 100.0 if evidence_quality_score > 1.0 else evidence_quality_score)
            ),
        )
        dimension_scores.append(
            DecisionUncertaintyDimensionScore(
                dimension=UncertaintyDimension.EVIDENCE_UNCERTAINTY,
                score=ev_unc,
                reasoning=f"Evidence quality rating: {evidence_quality_score:.2f}",
            )
        )

        # 3. Model uncertainty
        mod_unc = inputs.get(UncertaintyDimension.MODEL_UNCERTAINTY, 0.15)
        dimension_scores.append(
            DecisionUncertaintyDimensionScore(
                dimension=UncertaintyDimension.MODEL_UNCERTAINTY,
                score=mod_unc,
                reasoning="Evaluated from decision scoring model variance.",
            )
        )

        # 4. Context uncertainty
        ctx_unc = inputs.get(UncertaintyDimension.CONTEXT_UNCERTAINTY, 0.1)
        dimension_scores.append(
            DecisionUncertaintyDimensionScore(
                dimension=UncertaintyDimension.CONTEXT_UNCERTAINTY,
                score=ctx_unc,
                reasoning="Evaluated from cross-domain context coverage.",
            )
        )

        # 5. Conflicting signals
        conf_unc = min(1.0, conflicting_signal_count * 0.25)
        dimension_scores.append(
            DecisionUncertaintyDimensionScore(
                dimension=UncertaintyDimension.CONFLICTING_SIGNALS,
                score=conf_unc,
                reasoning=f"Identified {conflicting_signal_count} conflicting domain signals.",
            )
        )

        # 6. Insufficient evidence
        insuf_unc = inputs.get(UncertaintyDimension.INSUFFICIENT_EVIDENCE, 0.05)
        dimension_scores.append(
            DecisionUncertaintyDimensionScore(
                dimension=UncertaintyDimension.INSUFFICIENT_EVIDENCE,
                score=insuf_unc,
                reasoning="Evaluated from evidence gaps across required domain attributes.",
            )
        )

        # Overall average
        avg_unc = sum(ds.score for ds in dimension_scores) / len(dimension_scores)

        # Map level
        if avg_unc < 0.15:
            level = UncertaintyLevel.VERY_LOW
        elif avg_unc < 0.35:
            level = UncertaintyLevel.LOW
        elif avg_unc < 0.60:
            level = UncertaintyLevel.MODERATE
        elif avg_unc < 0.80:
            level = UncertaintyLevel.HIGH
        else:
            level = UncertaintyLevel.VERY_HIGH

        drivers = [ds.dimension.value for ds in dimension_scores if ds.score >= 0.3]
        mitigations = []
        if conf_unc >= 0.25:
            mitigations.append("Resolve conflicting domain signals via Unified Intelligence correlation.")
        if ev_unc >= 0.3:
            mitigations.append("Gather additional high-integrity evidence snapshots before decision execution.")

        assessment = DecisionUncertaintyAssessment(
            decision_id=decision_id,
            tenant_id=tenant_id,
            overall_uncertainty=round(avg_unc, 4),
            level=level,
            dimensions=dimension_scores,
            key_drivers=drivers,
            mitigation_recommendations=mitigations,
        )
        self._assessments[decision_id] = assessment
        return assessment

    def get_uncertainty_assessment(self, decision_id: str, tenant_id: str) -> DecisionUncertaintyAssessment:
        assessment = self._assessments.get(decision_id)
        if not assessment:
            raise DecisionNotFoundException(f"Uncertainty assessment for decision '{decision_id}' not found.")
        if assessment.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionIntelligenceException(
                f"Unauthorized cross-tenant access to uncertainty assessment for decision '{decision_id}'"
            )
        return assessment
