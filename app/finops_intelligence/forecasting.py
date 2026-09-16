"""Explainable Cost Forecasting Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class ForecastPeriod(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


class ForecastConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ForecastScenario(str, Enum):
    BASELINE = "BASELINE"
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"


class CostForecast(BaseModel):
    forecast_id: str = Field(default_factory=lambda: f"fcst_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    projected_spend_usd: float
    confidence: ForecastConfidence = ForecastConfidence.HIGH
    scenario: ForecastScenario = ForecastScenario.BASELINE
    period: ForecastPeriod = ForecastPeriod.MONTHLY
    reasoning: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ForecastManager:
    """Manages explainable cost forecasting and spending projections."""

    def __init__(self) -> None:
        self._forecasts: Dict[str, CostForecast] = {}

    def generate_forecast(
        self,
        tenant_id: str,
        historical_monthly_spend: List[float],
        scenario: ForecastScenario = ForecastScenario.BASELINE,
    ) -> CostForecast:
        avg = sum(historical_monthly_spend) / max(len(historical_monthly_spend), 1)
        multiplier = 1.0
        if scenario == ForecastScenario.OPTIMISTIC:
            multiplier = 0.85
        elif scenario == ForecastScenario.PESSIMISTIC:
            multiplier = 1.25

        projected = round(avg * multiplier, 2)
        reasoning = f"Projected from {len(historical_monthly_spend)} months history (avg: ${avg:.2f}) under {scenario.value} scenario."

        fcst = CostForecast(
            tenant_id=tenant_id,
            projected_spend_usd=projected,
            confidence=ForecastConfidence.HIGH if len(historical_monthly_spend) >= 3 else ForecastConfidence.MEDIUM,
            scenario=scenario,
            reasoning=reasoning,
        )
        self._forecasts[fcst.forecast_id] = fcst
        return fcst

    def get_forecast(self, tenant_id: str, forecast_id: str) -> CostForecast:
        fcst = self._forecasts.get(forecast_id)
        if not fcst or fcst.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return fcst
