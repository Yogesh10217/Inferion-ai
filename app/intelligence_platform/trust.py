"""Intelligence Trust Scoring Engine & Trust x Risk Matrix Evaluator."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.intelligence_platform.context import IntelligenceContext
from app.intelligence_platform.governance import IntelligencePolicyDecision, DecisionRiskAssessment
from app.governance_platform.risk import RiskLevel

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TrustDimension(str, Enum):
    EVIDENCE_QUALITY = "EVIDENCE_QUALITY"
    SOURCE_RELIABILITY = "SOURCE_RELIABILITY"
    DATA_FRESHNESS = "DATA_FRESHNESS"
    FORECAST_CONFIDENCE = "FORECAST_CONFIDENCE"
    SIMULATION_CONFIDENCE = "SIMULATION_CONFIDENCE"
    OUTCOME_HISTORY = "OUTCOME_HISTORY"
    POLICY_ALIGNMENT = "POLICY_ALIGNMENT"
    MODEL_RELIABILITY = "MODEL_RELIABILITY"


class IntelligenceTrustScore(BaseModel):
    trust_id: str = Field(default_factory=lambda: f"trust_{uuid.uuid4().hex[:10]}")
    overall_score: float = 85.0  # 0.0 to 100.0
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=_now)


class IntelligenceTrustEngine:
    """Evaluates multi-dimensional trust score and enforces Trust x Risk Decision Matrix."""

    def evaluate_trust(self, context: IntelligenceContext, forecast_confidence: float = 0.85, simulation_confidence: float = 0.90) -> IntelligenceTrustScore:
        ev_score = min(100.0, len(context.evidences) * 20.0 + 40.0) if context.evidences else 50.0
        sig_score = min(100.0, len(context.signals) * 15.0 + 50.0) if context.signals else 60.0
        fc_score = forecast_confidence * 100.0
        sim_score = simulation_confidence * 100.0

        dims = {
            TrustDimension.EVIDENCE_QUALITY.value: round(ev_score, 1),
            TrustDimension.SOURCE_RELIABILITY.value: round(sig_score, 1),
            TrustDimension.FORECAST_CONFIDENCE.value: round(fc_score, 1),
            TrustDimension.SIMULATION_CONFIDENCE.value: round(sim_score, 1),
            TrustDimension.DATA_FRESHNESS.value: 90.0,
            TrustDimension.POLICY_ALIGNMENT.value: 95.0,
        }

        overall = round(sum(dims.values()) / float(len(dims)), 1)
        return IntelligenceTrustScore(overall_score=overall, dimension_scores=dims)

    def evaluate_trust_risk_matrix(
        self,
        trust_score: float,
        risk_level: RiskLevel,
        policy_decision: IntelligencePolicyDecision,
        configurable_trust_threshold: float = 70.0,
    ) -> tuple[bool, str]:
        """
        Enforces Trust x Risk Decision Matrix:
        - High Trust + Low Risk -> Autonomous allowed
        - High Trust + Medium Risk -> Policy dependent
        - High Trust + High/Critical Risk -> Approval required
        - Medium Trust + Production Action -> Approval required
        - Low Trust + Any Action -> Blocked / Human review
        """
        if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            return False, f"Risk level {risk_level.value} requires explicit human approval."

        if trust_score < 50.0:
            return False, f"Trust score {trust_score:.1f} is LOW (<50.0); autonomous execution blocked."

        if trust_score < configurable_trust_threshold:
            return False, f"Trust score {trust_score:.1f} is below configured threshold {configurable_trust_threshold:.1f}; human review required."

        if policy_decision == IntelligencePolicyDecision.REQUIRE_APPROVAL:
            return False, "Policy decision requires explicit approval."

        if policy_decision == IntelligencePolicyDecision.BLOCK:
            return False, "Policy decision BLOCKED execution."

        return True, "Autonomous execution allowed under Trust x Risk Decision Matrix."
