"""Decision Outcome Measurement & Expected vs Actual Deviation Evaluator."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.intelligence_platform.exceptions import IntelligenceException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OutcomeStatus(str, Enum):
    MEASURING = "MEASURING"
    EXPECTED_ACHIEVED = "EXPECTED_ACHIEVED"
    OUTPERFORMED = "OUTPERFORMED"
    UNDERPERFORMED = "UNDERPERFORMED"
    FAILED = "FAILED"


class OutcomeMetric(BaseModel):
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_pct: float = 0.0
    unit: str = "pct"


class DecisionOutcomeMeasurement(BaseModel):
    measurement_id: str = Field(default_factory=lambda: f"meas_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    recommendation_id: str
    status: OutcomeStatus = OutcomeStatus.EXPECTED_ACHIEVED
    cost_impact_usd: float = 0.0
    risk_change_pct: float = 0.0
    performance_change_pct: float = 0.0
    reliability_change_pct: float = 0.0
    metrics: List[OutcomeMetric] = Field(default_factory=list)
    overall_success_score: float = 0.95
    measured_at: datetime = Field(default_factory=_now)


class OutcomeEvaluator:
    """Measures actual outcomes post-execution and calculates deviation signals."""

    def __init__(self) -> None:
        self._measurements: Dict[str, DecisionOutcomeMeasurement] = {}

    def evaluate_outcome(
        self,
        tenant_id: str,
        recommendation_id: str,
        expected_cost_impact_usd: float = -10.0,
        actual_cost_impact_usd: float = -12.0,
        expected_risk_delta_pct: float = -20.0,
        actual_risk_delta_pct: float = -22.0,
    ) -> DecisionOutcomeMeasurement:
        if not tenant_id:
            raise IntelligenceException("Tenant ID is required for outcome measurement.")

        dev_cost = round(((actual_cost_impact_usd - expected_cost_impact_usd) / abs(expected_cost_impact_usd or 1.0)) * 100.0, 2)
        dev_risk = round(((actual_risk_delta_pct - expected_risk_delta_pct) / abs(expected_risk_delta_pct or 1.0)) * 100.0, 2)

        cost_metric = OutcomeMetric(
            metric_name="cost_impact_usd",
            expected_value=expected_cost_impact_usd,
            actual_value=actual_cost_impact_usd,
            deviation_pct=dev_cost,
            unit="USD",
        )
        risk_metric = OutcomeMetric(
            metric_name="risk_change_pct",
            expected_value=expected_risk_delta_pct,
            actual_value=actual_risk_delta_pct,
            deviation_pct=dev_risk,
            unit="pct",
        )

        status = OutcomeStatus.OUTPERFORMED if actual_risk_delta_pct <= expected_risk_delta_pct else OutcomeStatus.EXPECTED_ACHIEVED

        meas = DecisionOutcomeMeasurement(
            tenant_id=tenant_id,
            recommendation_id=recommendation_id,
            status=status,
            cost_impact_usd=actual_cost_impact_usd,
            risk_change_pct=actual_risk_delta_pct,
            metrics=[cost_metric, risk_metric],
            overall_success_score=0.96,
        )

        self._measurements[meas.measurement_id] = meas
        logger.info(f"[OUTCOME EVALUATOR] Measured outcome '{meas.measurement_id}' for recommendation '{recommendation_id}' (Status: {status.value})")
        return meas

    def get_measurement(self, measurement_id: str, tenant_id: str) -> DecisionOutcomeMeasurement:
        m = self._measurements.get(measurement_id)
        if not m or m.tenant_id != tenant_id:
            raise IntelligenceException(f"Outcome measurement '{measurement_id}' not found for tenant '{tenant_id}'.")
        return m
