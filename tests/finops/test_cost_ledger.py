"""Unit tests for Unified Cost Ledger and Decimal precision."""

from decimal import Decimal

from app.finops.cost_ledger import CostCategory, UnifiedCostLedger


def test_cost_ledger_decimal_precision_and_adjustments():
    ledger = UnifiedCostLedger()

    # 1. Record cost with Decimal
    e1 = ledger.record_cost(
        component="GATEWAY",
        cost_category=CostCategory.MODEL_INFERENCE,
        quantity=Decimal("1000"),
        unit_price=Decimal("0.00003"),
        tenant_id="tenant_fin",
    )

    assert isinstance(e1.total_cost, Decimal)
    assert e1.total_cost == Decimal("0.030000")

    # 2. Immutable history - adjustments create CostAdjustment
    adj = ledger.record_adjustment(
        original_cost_id=e1.cost_id,
        adjustment_amount=Decimal("-0.005000"),
        reason="Volume discount credit",
        tenant_id="tenant_fin",
    )
    assert isinstance(adj.adjustment_amount, Decimal)

    # 3. Total cost includes adjustment
    total = ledger.get_total_cost(tenant_id="tenant_fin")
    assert total == Decimal("0.025000")
