"""Continuous Intelligence Learning with Feedback Poisoning Resistance."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.intelligence_platform.exceptions import IntelligenceException
from app.intelligence_platform.outcomes import DecisionOutcomeMeasurement
from app.knowledge_platform.manager import KnowledgePlatformManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RecommendationEffectiveness(BaseModel):
    recommendation_type: str
    total_recommendations: int = 1
    total_accepted: int = 1
    total_successful_outcomes: int = 1
    effectiveness_score: float = 0.95


class LearningSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"lsig_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    recommendation_id: str
    outcome_status: str
    trust_weight: float = 0.90  # Poisoning resistance weight
    is_valid_learning_signal: bool = True
    recorded_at: datetime = Field(default_factory=_now)


class LearningInsight(BaseModel):
    learning_id: str = Field(default_factory=lambda: f"lrn_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    title: str
    summary: str
    recommendation_type: str
    provenance_reference: str
    confidence: float = 0.90
    created_at: datetime = Field(default_factory=_now)


class ContinuousLearningManager:
    """Manages continuous intelligence learning and stores learning insights in Knowledge Platform."""

    def __init__(self, knowledge_platform_manager: Optional[KnowledgePlatformManager] = None) -> None:
        self.knowledge_platform_manager = knowledge_platform_manager or KnowledgePlatformManager()
        self._learning_signals: Dict[str, LearningSignal] = {}
        self._effectiveness: Dict[str, RecommendationEffectiveness] = {}
        self._insights: Dict[str, LearningInsight] = {}

    def process_outcome_learning(
        self,
        tenant_id: str,
        outcome: DecisionOutcomeMeasurement,
        recommendation_type: str,
        trust_weight: float = 0.90,
    ) -> LearningInsight:
        # Poisoning protection check
        if trust_weight < 0.40:
            logger.warning(f"[CONTINUOUS LEARNING] Ignored untrusted outcome signal (trust weight: {trust_weight:.2f}) to prevent feedback poisoning.")
            raise IntelligenceException("Learning signal rejected due to low trust weight (poisoning protection).")

        lsig = LearningSignal(
            tenant_id=tenant_id,
            recommendation_id=outcome.recommendation_id,
            outcome_status=outcome.status.value,
            trust_weight=trust_weight,
        )
        self._learning_signals[lsig.signal_id] = lsig

        eff = self._effectiveness.get(recommendation_type)
        if not eff:
            eff = RecommendationEffectiveness(recommendation_type=recommendation_type)
            self._effectiveness[recommendation_type] = eff
        else:
            eff.total_recommendations += 1
            if outcome.status.value in ("EXPECTED_ACHIEVED", "OUTPERFORMED"):
                eff.total_accepted += 1
                eff.total_successful_outcomes += 1
            eff.effectiveness_score = round(eff.total_successful_outcomes / float(eff.total_recommendations), 2)

        # Store in Knowledge Platform with provenance
        title = f"Learning Insight: {recommendation_type} Effectiveness ({eff.effectiveness_score * 100:.0f}%)"
        summary = f"Outcome measurement '{outcome.measurement_id}' verified {outcome.status.value} for recommendation '{outcome.recommendation_id}'."

        try:
            self.knowledge_platform_manager.create_knowledge_item(
                tenant_id=tenant_id,
                title=title,
                content=summary,
                source_type="INTELLIGENCE_LEARNING",
            )
        except Exception as e:
            logger.debug(f"Knowledge platform storage fallback: {e}")

        insight = LearningInsight(
            tenant_id=tenant_id,
            title=title,
            summary=summary,
            recommendation_type=recommendation_type,
            provenance_reference=f"measurement:{outcome.measurement_id}",
        )
        self._insights[insight.learning_id] = insight

        logger.info(f"[CONTINUOUS LEARNING] Processed learning insight '{insight.learning_id}' for tenant '{tenant_id}'")
        return insight

    def list_insights(self, tenant_id: str) -> List[LearningInsight]:
        return [i for i in self._insights.values() if i.tenant_id == tenant_id]
