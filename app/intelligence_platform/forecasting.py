"""Provider-Based Predictive Analytics & Forecasting Engine."""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.intelligence_platform.context import IntelligenceContext
from app.intelligence_platform.exceptions import IntelligenceException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ForecastType(str, Enum):
    COST_FORECAST = "COST_FORECAST"
    CAPACITY_FORECAST = "CAPACITY_FORECAST"
    INCIDENT_RISK_FORECAST = "INCIDENT_RISK_FORECAST"
    SLO_BREACH_FORECAST = "SLO_BREACH_FORECAST"
    MODEL_DEGRADATION_FORECAST = "MODEL_DEGRADATION_FORECAST"
    DEMAND_FORECAST = "DEMAND_FORECAST"
    RESOURCE_EXHAUSTION_FORECAST = "RESOURCE_EXHAUSTION_FORECAST"


class ForecastHorizon(str, Enum):
    NEAR_TERM = "NEAR_TERM"  # 1-6 hours
    SHORT_TERM = "SHORT_TERM"  # 24-72 hours
    MEDIUM_TERM = "MEDIUM_TERM"  # 7-30 days
    LONG_TERM = "LONG_TERM"  # 90+ days


class ForecastConfidence(BaseModel):
    confidence_score: float = 0.85
    lower_bound: float = 0.70
    upper_bound: float = 0.95
    is_fact: bool = False  # Always explicitly false to distinguish forecast from fact


class Forecast(BaseModel):
    forecast_id: str = Field(default_factory=lambda: f"fc_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    target_resource_id: str
    forecast_type: ForecastType
    horizon: ForecastHorizon = ForecastHorizon.NEAR_TERM
    predicted_value: float
    unit: str = "percentage"
    summary: str
    confidence: ForecastConfidence = Field(default_factory=ForecastConfidence)
    evidence_window_hours: int = 24
    provider_name: str = "DeterministicForecastProvider"
    generated_at: datetime = Field(default_factory=_now)


class ForecastProvider(ABC):
    """Abstract interface for forecasting solvers/providers."""

    @abstractmethod
    def generate_forecast(
        self,
        tenant_id: str,
        target_resource_id: str,
        forecast_type: ForecastType,
        context: IntelligenceContext,
        horizon: ForecastHorizon = ForecastHorizon.NEAR_TERM,
    ) -> Forecast:
        pass


class DeterministicForecastProvider(ForecastProvider):
    """Deterministic baseline forecasting provider."""

    def generate_forecast(
        self,
        tenant_id: str,
        target_resource_id: str,
        forecast_type: ForecastType,
        context: IntelligenceContext,
        horizon: ForecastHorizon = ForecastHorizon.NEAR_TERM,
    ) -> Forecast:
        # Base forecast computation from signals
        signal_count = len(context.signals)
        high_severity_count = sum(1 for s in context.signals if s.classification.value in ("WARNING", "CRITICAL_ALERT"))

        base_risk = min(0.95, 0.15 + (high_severity_count * 0.25) + (signal_count * 0.05))

        if forecast_type == ForecastType.COST_FORECAST:
            pred_val = 1500.0 * (1.0 + base_risk)
            unit = "USD"
            summary = f"Projected cost under current load: ${pred_val:.2f}"
        elif forecast_type == ForecastType.RESOURCE_EXHAUSTION_FORECAST:
            pred_val = min(100.0, 70.0 + (base_risk * 30.0))
            unit = "percent_utilization"
            summary = f"Projected capacity utilization: {pred_val:.1f}%"
        elif forecast_type == ForecastType.INCIDENT_RISK_FORECAST:
            pred_val = base_risk * 100.0
            unit = "probability_pct"
            summary = f"Incident risk probability within horizon: {pred_val:.1f}%"
        else:
            pred_val = base_risk * 100.0
            unit = "index"
            summary = f"Projected trend index: {pred_val:.1f}"

        conf = ForecastConfidence(
            confidence_score=round(max(0.60, 0.90 - (base_risk * 0.20)), 2),
            lower_bound=round(pred_val * 0.85, 2),
            upper_bound=round(pred_val * 1.15, 2),
            is_fact=False,
        )

        return Forecast(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            forecast_type=forecast_type,
            horizon=horizon,
            predicted_value=pred_val,
            unit=unit,
            summary=summary,
            confidence=conf,
            provider_name="DeterministicForecastProvider",
        )


class ForecastEngine:
    """Orchestrates forecast providers."""

    def __init__(self, provider: Optional[ForecastProvider] = None) -> None:
        self.provider = provider or DeterministicForecastProvider()
        self._forecasts: Dict[str, Forecast] = {}

    def forecast(
        self,
        tenant_id: str,
        target_resource_id: str,
        forecast_type: ForecastType,
        context: IntelligenceContext,
        horizon: ForecastHorizon = ForecastHorizon.NEAR_TERM,
    ) -> Forecast:
        if not tenant_id:
            raise IntelligenceException("Tenant ID is required for forecasting.")

        fc = self.provider.generate_forecast(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            forecast_type=forecast_type,
            context=context,
            horizon=horizon,
        )
        self._forecasts[fc.forecast_id] = fc
        logger.info(f"[FORECAST ENGINE] Generated {forecast_type.value} '{fc.forecast_id}' for tenant '{tenant_id}'")
        return fc

    def get_forecast(self, forecast_id: str, tenant_id: str) -> Forecast:
        fc = self._forecasts.get(forecast_id)
        if not fc or fc.tenant_id != tenant_id:
            raise IntelligenceException(f"Forecast '{forecast_id}' not found for tenant '{tenant_id}'.")
        return fc
