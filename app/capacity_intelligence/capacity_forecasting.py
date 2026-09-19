"""Capacity forecasting engine for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import CapacityForecast
from app.capacity_intelligence.repositories import ForecastRepository

logger = logging.getLogger(__name__)


class CapacityForecastEngine:
    """Predicts future resource utilization and capacity exhaustion timelines using explainable deterministic linear growth models."""

    def __init__(self, repo: ForecastRepository) -> None:
        self.repo = repo

    def forecast_capacity(
        self,
        tenant_id: str,
        resource_id: str,
        current_utilization_pct: float = 65.0,
        growth_rate_pct_per_day: float = 1.2,
        horizon_days: int = 30,
    ) -> CapacityForecast:
        predicted_util = min(100.0, current_utilization_pct + (growth_rate_pct_per_day * horizon_days))
        exhaustion_days = None
        if growth_rate_pct_per_day > 0:
            remaining_headroom = 100.0 - current_utilization_pct
            exhaustion_days = max(1, int(remaining_headroom / growth_rate_pct_per_day))

        forecast = CapacityForecast(
            tenant_id=tenant_id,
            resource_id=resource_id,
            forecast_horizon_days=horizon_days,
            predicted_utilization_pct=round(predicted_util, 2),
            estimated_exhaustion_days=exhaustion_days,
            confidence_score=0.92,
        )
        self.repo.save(forecast)
        logger.info(
            f"Generated CapacityForecast for resource '{resource_id}': Predicted={predicted_util:.2f}% in {horizon_days}d"
        )
        return forecast
