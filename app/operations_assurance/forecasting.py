"""Operational forecasting scenarios: BASELINE, OPTIMISTIC, PESSIMISTIC, HIGH_DEMAND, FAILURE_SCENARIO, CUSTOM."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ForecastScenario(str, Enum):
    BASELINE = "BASELINE"
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"
    HIGH_DEMAND = "HIGH_DEMAND"
    FAILURE_SCENARIO = "FAILURE_SCENARIO"
    CUSTOM = "CUSTOM"


class OperationalForecast(BaseModel):
    forecast_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    scenario: ForecastScenario
    horizon_days: int = 30
    projected_capacity_utilization: float = 0.5
    failure_probability: float = 0.05
    incident_probability: float = 0.1
    predicted_service_degradation_risk: float = 0.05
    projected_demand_tps: float = 200.0
    projected_resource_pressure: float = 0.4
    advisory_notes: str = ""
    auto_execute: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsForecastingEngine:
    """Generates analytical, advisory operational forecasting models."""

    def __init__(self) -> None:
        self._forecasts: Dict[str, Dict[str, OperationalForecast]] = {}  # tenant_id -> {forecast_id: forecast}

    def generate_forecast(
        self,
        tenant_id: str,
        service_id: str,
        scenario: ForecastScenario = ForecastScenario.BASELINE,
        horizon_days: int = 30,
        baseline_tps: float = 200.0,
    ) -> OperationalForecast:
        multiplier = 1.0
        if scenario == ForecastScenario.HIGH_DEMAND:
            multiplier = 2.5
        elif scenario == ForecastScenario.PESSIMISTIC:
            multiplier = 1.5
        elif scenario == ForecastScenario.OPTIMISTIC:
            multiplier = 0.8
        elif scenario == ForecastScenario.FAILURE_SCENARIO:
            multiplier = 1.2

        demand_tps = baseline_tps * multiplier
        capacity_util = min(1.0, 0.4 * multiplier)
        fail_prob = min(0.95, 0.05 * (multiplier**1.5))
        inc_prob = min(0.95, 0.1 * multiplier)

        forecast = OperationalForecast(
            tenant_id=tenant_id,
            service_id=service_id,
            scenario=scenario,
            horizon_days=horizon_days,
            projected_capacity_utilization=round(capacity_util, 3),
            failure_probability=round(fail_prob, 3),
            incident_probability=round(inc_prob, 3),
            predicted_service_degradation_risk=round(min(1.0, fail_prob * 1.2), 3),
            projected_demand_tps=round(demand_tps, 1),
            projected_resource_pressure=round(min(1.0, capacity_util * 1.1), 3),
            advisory_notes=f"Forecast under scenario {scenario.value} over {horizon_days} days. Analytical advice only.",
            auto_execute=False,
        )

        if tenant_id not in self._forecasts:
            self._forecasts[tenant_id] = {}
        self._forecasts[tenant_id][forecast.forecast_id] = forecast
        return forecast

    def list_forecasts(self, tenant_id: str, service_id: Optional[str] = None) -> List[OperationalForecast]:
        tenant_forecasts = self._forecasts.get(tenant_id, {})
        if service_id:
            return [f for f in tenant_forecasts.values() if f.service_id == service_id]
        return list(tenant_forecasts.values())
