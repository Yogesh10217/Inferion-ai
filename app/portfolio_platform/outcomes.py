"""Initiative Outcome Evaluation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class OutcomeStatus(str, Enum):
    EXCEEDED_EXPECTATIONS = "EXCEEDED_EXPECTATIONS"
    MET_EXPECTATIONS = "MET_EXPECTATIONS"
    BELOW_EXPECTATIONS = "BELOW_EXPECTATIONS"
    FAILED = "FAILED"


class OutcomeDeviation(BaseModel):
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_percentage: float


class InitiativeOutcome(BaseModel):
    outcome_id: str = Field(default_factory=lambda: f"out_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    status: OutcomeStatus = OutcomeStatus.MET_EXPECTATIONS
    expected_cost_usd: float
    actual_cost_usd: float
    expected_benefit_usd: float
    actual_benefit_usd: float
    expected_roi_pct: float
    actual_roi_pct: float
    deviations: List[OutcomeDeviation] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OutcomeEvaluator:
    """Evaluates initiative outcomes by comparing expected vs actual metrics."""

    def evaluate_outcome(
        self,
        tenant_id: str,
        initiative_id: str,
        expected_cost_usd: float,
        actual_cost_usd: float,
        expected_benefit_usd: float,
        actual_benefit_usd: float,
    ) -> InitiativeOutcome:
        exp_roi = ((expected_benefit_usd - expected_cost_usd) / max(1.0, expected_cost_usd)) * 100.0
        act_roi = ((actual_benefit_usd - actual_cost_usd) / max(1.0, actual_cost_usd)) * 100.0

        deviations = [
            OutcomeDeviation(
                metric_name="cost_usd",
                expected_value=expected_cost_usd,
                actual_value=actual_cost_usd,
                deviation_percentage=((actual_cost_usd - expected_cost_usd) / max(1.0, expected_cost_usd)) * 100.0,
            ),
            OutcomeDeviation(
                metric_name="benefit_usd",
                expected_value=expected_benefit_usd,
                actual_value=actual_benefit_usd,
                deviation_percentage=((actual_benefit_usd - expected_benefit_usd) / max(1.0, expected_benefit_usd))
                * 100.0,
            ),
        ]

        if act_roi >= exp_roi * 1.1:
            status = OutcomeStatus.EXCEEDED_EXPECTATIONS
        elif act_roi >= exp_roi * 0.9:
            status = OutcomeStatus.MET_EXPECTATIONS
        elif act_roi >= 0.0:
            status = OutcomeStatus.BELOW_EXPECTATIONS
        else:
            status = OutcomeStatus.FAILED

        return InitiativeOutcome(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            status=status,
            expected_cost_usd=expected_cost_usd,
            actual_cost_usd=actual_cost_usd,
            expected_benefit_usd=expected_benefit_usd,
            actual_benefit_usd=actual_benefit_usd,
            expected_roi_pct=exp_roi,
            actual_roi_pct=act_roi,
            deviations=deviations,
        )
