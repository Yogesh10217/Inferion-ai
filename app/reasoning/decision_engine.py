"""
Planning & Strategy Decision Engine
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class StrategyOption(BaseModel):
    name: str
    description: str
    estimated_cost: float
    estimated_duration_seconds: float
    risk_level: str = "low"  # low, medium, high
    confidence_score: float = 0.9


class DecisionOutcome(BaseModel):
    selected_option: StrategyOption
    rationale: str
    tradeoff_summary: Dict[str, Any] = Field(default_factory=dict)


class PlanningDecisionEngine:
    """Evaluates strategy options and selects the optimal path based on risk, cost, and confidence."""

    @staticmethod
    def evaluate_strategies(options: List[StrategyOption], max_risk_allowed: str = "high") -> DecisionOutcome:
        if not options:
            raise ValueError("No strategy options provided for evaluation")

        risk_scores = {"low": 1, "medium": 2, "high": 3}
        max_r_val = risk_scores.get(max_risk_allowed.lower(), 3)

        valid_options = [o for o in options if risk_scores.get(o.risk_level.lower(), 1) <= max_r_val]
        if not valid_options:
            valid_options = options

        # Pick option with highest utility score: (confidence / (cost * duration))
        best_opt = max(valid_options, key=lambda o: (o.confidence_score / (max(0.001, o.estimated_cost) * max(1.0, o.estimated_duration_seconds))))

        outcome = DecisionOutcome(
            selected_option=best_opt,
            rationale=f"Selected '{best_opt.name}' offering confidence {best_opt.confidence_score:.2f} at cost ${best_opt.estimated_cost:.4f}",
            tradeoff_summary={"evaluated_options_count": len(options), "selected": best_opt.name},
        )
        logger.info(f"[DECISION ENGINE] {outcome.rationale}")
        return outcome
