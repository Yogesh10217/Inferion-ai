"""Unit tests for Provider-Based Predictive Analytics & Forecasting Engine."""

from app.intelligence_platform.context import ContextBuilder
from app.intelligence_platform.forecasting import DeterministicForecastProvider, ForecastEngine, ForecastType


def test_provider_based_forecasting():
    ctx = ContextBuilder().assemble_context("t1", primary_resource_id="svc_capacity")
    engine = ForecastEngine(provider=DeterministicForecastProvider())

    fc = engine.forecast("t1", "svc_capacity", ForecastType.CAPACITY_FORECAST, ctx)

    assert fc.forecast_id.startswith("fc_")
    assert fc.confidence.is_fact is False  # Explicitly distinguished from fact
    assert fc.predicted_value > 0
    assert fc.provider_name == "DeterministicForecastProvider"
