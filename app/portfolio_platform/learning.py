"""Continuous Portfolio Learning & Intelligence Feedback Subsystem."""

import uuid
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.portfolio_platform.outcomes import InitiativeOutcome


class LearningSignalType(str, Enum):
    OUTCOME_DEVIATION = "OUTCOME_DEVIATION"
    COST_OVERRUN = "COST_OVERRUN"
    BENEFIT_SURPLUS = "BENEFIT_SURPLUS"
    STRATEGY_FEEDBACK = "STRATEGY_FEEDBACK"


class PortfolioRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_area: str  # PRIORITIZATION, COST_ESTIMATION, STRATEGY
    suggestion: str
    confidence_score: float = 85.0


class PortfolioLearningManager:
    """Processes historical outcomes and generates strategic feedback signals."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, List[PortfolioRecommendation]] = {}

    def process_outcome_learning(self, tenant_id: str, outcome: InitiativeOutcome) -> PortfolioRecommendation:
        if outcome.actual_cost_usd > outcome.expected_cost_usd * 1.2:
            sug = f"Adjust cost estimation multiplier for initiative '{outcome.initiative_id}' due to {outcome.actual_cost_usd / outcome.expected_cost_usd:.2f}x overrun."
            target = "COST_ESTIMATION"
        elif outcome.actual_benefit_usd > outcome.expected_benefit_usd * 1.2:
            sug = f"Upweight prioritization score for high-performing category of initiative '{outcome.initiative_id}'."
            target = "PRIORITIZATION"
        else:
            sug = f"Initiative '{outcome.initiative_id}' met expectations cleanly; baseline weights validated."
            target = "STRATEGY"

        rec = PortfolioRecommendation(
            tenant_id=tenant_id,
            target_area=target,
            suggestion=sug,
            confidence_score=90.0,
        )

        if tenant_id not in self._recommendations:
            self._recommendations[tenant_id] = []
        self._recommendations[tenant_id].append(rec)
        return rec

    def list_recommendations(self, tenant_id: str) -> List[PortfolioRecommendation]:
        return self._recommendations.get(tenant_id, [])
