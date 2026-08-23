"""Decision Outcome Monitoring Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class OutcomeStatus(str, Enum):
    ACHIEVED = "ACHIEVED"
    PARTIALLY_ACHIEVED = "PARTIALLY_ACHIEVED"
    NOT_ACHIEVED = "NOT_ACHIEVED"
    EXCEEDED = "EXCEEDED"
    REGRESSED = "REGRESSED"


class OutcomeDeviation(BaseModel):
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_pct: float


class DecisionOutcome(BaseModel):
    outcome_id: str = Field(default_factory=lambda: f"out_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    decision_id: str
    status: OutcomeStatus = OutcomeStatus.ACHIEVED
    expected_value_usd: float
    actual_value_usd: float
    deviations: List[OutcomeDeviation] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionOutcomeManager:
    """Monitors and compares expected vs observed decision outcomes."""

    def record_outcome(
        self,
        tenant_id: str,
        decision_id: str,
        expected_value_usd: float,
        actual_value_usd: float,
    ) -> DecisionOutcome:
        dev_pct = ((actual_value_usd - expected_value_usd) / max(1.0, expected_value_usd)) * 100.0

        if actual_value_usd >= expected_value_usd * 1.1:
            status = OutcomeStatus.EXCEEDED
        elif actual_value_usd >= expected_value_usd * 0.9:
            status = OutcomeStatus.ACHIEVED
        elif actual_value_usd >= expected_value_usd * 0.5:
            status = OutcomeStatus.PARTIALLY_ACHIEVED
        else:
            status = OutcomeStatus.NOT_ACHIEVED

        deviation = OutcomeDeviation(
            metric_name="value_usd",
            expected_value=expected_value_usd,
            actual_value=actual_value_usd,
            deviation_pct=dev_pct,
        )

        return DecisionOutcome(
            tenant_id=tenant_id,
            decision_id=decision_id,
            status=status,
            expected_value_usd=expected_value_usd,
            actual_value_usd=actual_value_usd,
            deviations=[deviation],
        )
