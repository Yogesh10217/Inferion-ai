"""Deterministic Decision Explainability Engine."""

import logging
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.intelligence_platform.decisions import Decision
from app.intelligence_platform.recommendations import Recommendation

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceExplanation(BaseModel):
    source: str
    summary: str
    relevance_score: float


class AlternativeExplanation(BaseModel):
    name: str
    rejection_reason: str
    cost_usd: float
    risk_level: str


class RiskExplanation(BaseModel):
    risk_level: str
    mitigation_strategy: str
    requires_approval: bool


class RecommendationExplanation(BaseModel):
    recommendation_id: str
    why_recommended: str
    supporting_evidence: List[EvidenceExplanation] = Field(default_factory=list)
    alternatives_considered: List[AlternativeExplanation] = Field(default_factory=list)
    risk_summary: RiskExplanation
    assumptions: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    invalidation_triggers: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=_now)


class ExplainabilityEngine:
    """Generates structured deterministic explanations from decision artifacts."""

    def generate_explanation(self, decision: Decision, recommendation: Recommendation) -> RecommendationExplanation:
        why = (
            f"Action '{recommendation.action_description}' was selected because it satisfied "
            f"primary objective '{decision.criteria.primary_objective}' with confidence score {recommendation.confidence_score:.2f}."
        )

        evidence_list = [
            EvidenceExplanation(
                source="OperationalSignals",
                summary=f"Signal for target resource {recommendation.target_resource_id}",
                relevance_score=0.92,
            )
        ]

        alternatives = []
        for opt in decision.options:
            if not opt.is_selected:
                alternatives.append(
                    AlternativeExplanation(
                        name=opt.title,
                        rejection_reason=f"Higher risk ({opt.expected_risk}) or inferior objective alignment.",
                        cost_usd=opt.expected_cost_usd,
                        risk_level=opt.expected_risk,
                    )
                )

        risk_summary = RiskExplanation(
            risk_level=recommendation.risk_level,
            mitigation_strategy="Automated verification and rollback control",
            requires_approval=recommendation.risk_level in ("HIGH", "CRITICAL"),
        )

        assumptions = [
            "Baseline metric trends remain stable over horizon",
            "Downstream service dependencies remain healthy",
        ]
        uncertainties = [
            "External traffic spikes could affect latency estimate",
        ]
        invalidation_triggers = [
            "Signal confidence drops below 0.70",
            "Service health drops to UNHEALTHY prior to execution",
        ]

        exp = RecommendationExplanation(
            recommendation_id=recommendation.recommendation_id,
            why_recommended=why,
            supporting_evidence=evidence_list,
            alternatives_considered=alternatives,
            risk_summary=risk_summary,
            assumptions=assumptions,
            uncertainties=uncertainties,
            invalidation_triggers=invalidation_triggers,
        )

        logger.info(
            f"[EXPLAINABILITY ENGINE] Generated deterministic explanation for recommendation '{recommendation.recommendation_id}'"
        )
        return exp
