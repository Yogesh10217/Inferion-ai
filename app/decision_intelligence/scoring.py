"""Deterministic Multi-Factor Decision Scoring Engine."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class DecisionScoreDimension(str, Enum):
    BUSINESS_VALUE = "BUSINESS_VALUE"
    COST_EFFICIENCY = "COST_EFFICIENCY"
    RISK = "RISK"
    TRUST = "TRUST"
    COMPLIANCE = "COMPLIANCE"
    STRATEGIC_ALIGNMENT = "STRATEGIC_ALIGNMENT"
    ARCHITECTURE_FIT = "ARCHITECTURE_FIT"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    OPERATIONAL_FEASIBILITY = "OPERATIONAL_FEASIBILITY"
    CONFIDENCE = "CONFIDENCE"


class DecisionScoringModel(BaseModel):
    model_id: str = Field(default_factory=lambda: f"scormod_{uuid.uuid4().hex[:12]}")
    version: str = "1.0.0"
    weights: Dict[DecisionScoreDimension, float] = Field(
        default_factory=lambda: {
            DecisionScoreDimension.BUSINESS_VALUE: 0.15,
            DecisionScoreDimension.COST_EFFICIENCY: 0.10,
            DecisionScoreDimension.RISK: 0.15,
            DecisionScoreDimension.TRUST: 0.15,
            DecisionScoreDimension.COMPLIANCE: 0.15,
            DecisionScoreDimension.STRATEGIC_ALIGNMENT: 0.10,
            DecisionScoreDimension.ARCHITECTURE_FIT: 0.10,
            DecisionScoreDimension.OPERATIONAL_FEASIBILITY: 0.10,
        }
    )


class DecisionScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"score_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    overall_score: float
    dimension_scores: Dict[DecisionScoreDimension, float]
    model_version: str = "1.0.0"
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionScoringEngine:
    """Computes deterministic multi-factor decision scores without overriding hard constraints."""

    def __init__(self, scoring_model: Optional[DecisionScoringModel] = None) -> None:
        self.scoring_model = scoring_model or DecisionScoringModel()

    def compute_score(
        self,
        tenant_id: str,
        context_id: str,
        dimension_scores: Dict[DecisionScoreDimension, float],
    ) -> DecisionScore:
        weights = self.scoring_model.weights
        total_weight = sum(weights.values())
        weighted_sum = 0.0

        for dim, w in weights.items():
            val = dimension_scores.get(dim, 50.0)
            weighted_sum += val * w

        overall = weighted_sum / max(0.0001, total_weight)
        overall = max(0.0, min(100.0, overall))

        return DecisionScore(
            tenant_id=tenant_id,
            context_id=context_id,
            overall_score=overall,
            dimension_scores=dimension_scores,
            model_version=self.scoring_model.version,
        )
