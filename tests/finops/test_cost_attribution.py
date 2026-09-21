"""Unit tests for CostAttributionEngine."""

from decimal import Decimal

from app.finops.attribution import CostAttributionEngine
from app.finops.cost_ledger import CostCategory, UnifiedCostLedger


def test_hierarchical_cost_attribution_and_shared_allocation():
    ledger = UnifiedCostLedger()
    ledger.record_cost(
        "GATEWAY", CostCategory.MODEL_INFERENCE, Decimal("1.0"), Decimal("10.0"), tenant_id="tenant_attr"
    )

    engine = CostAttributionEngine(ledger=ledger)
    summary = engine.attribute_tenant_costs("tenant_attr")

    assert summary.direct_cost == Decimal("10.000000")
    assert summary.allocated_shared_cost == Decimal("0.500000")  # 5% overhead
    assert summary.total_attributed_cost == Decimal("10.500000")
