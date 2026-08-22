"""Unit tests for CostForecastingEngine."""

from decimal import Decimal
import pytest
from app.finops.cost_ledger import UnifiedCostLedger, CostCategory
from app.finops.forecasting import CostForecastingEngine, ForecastStrategy


def test_cost_forecasting_and_budget_exhaustion_prediction():
    ledger = UnifiedCostLedger()
    ledger.record_cost("GATEWAY", CostCategory.MODEL_INFERENCE, Decimal("1.0"), Decimal("10.0"), tenant_id="tenant_fc")

    engine = CostForecastingEngine(ledger=ledger)
    fc = engine.forecast_spend(tenant_id="tenant_fc", current_budget_limit=Decimal("500.0"))

    assert isinstance(fc.projected_monthly_cost, Decimal)
    assert fc.projected_monthly_cost > Decimal("0.0")
    assert fc.estimated_budget_exhaustion_days is not None
