"""Unit tests for CostAnalyticsEngine."""

from decimal import Decimal

from app.finops.analytics import CostAnalyticsEngine
from app.finops.cost_ledger import CostCategory, UnifiedCostLedger


def test_cost_analytics_reporting_and_breakdown():
    ledger = UnifiedCostLedger()
    ledger.record_cost("GATEWAY", CostCategory.MODEL_INFERENCE, Decimal("1.0"), Decimal("15.0"), tenant_id="tenant_an")
    ledger.record_cost("TOOL", CostCategory.TOOL_EXECUTION, Decimal("1.0"), Decimal("5.0"), tenant_id="tenant_an")

    engine = CostAnalyticsEngine(ledger=ledger)
    rep = engine.generate_report("tenant_an")

    assert rep.total_cost == Decimal("20.000000")
    assert rep.cost_per_execution == Decimal("10.000000")
    assert len(rep.cost_by_category) == 2
