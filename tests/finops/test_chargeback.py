"""Unit tests for ChargebackManager and internal showback."""

from decimal import Decimal
import pytest
from app.finops.cost_ledger import UnifiedCostLedger, CostCategory
from app.finops.chargeback import ChargebackManager


def test_showback_reporting():
    ledger = UnifiedCostLedger()
    ledger.record_cost("GATEWAY", CostCategory.MODEL_INFERENCE, Decimal("1.0"), Decimal("100.0"), tenant_id="tenant_cb")

    mgr = ChargebackManager(ledger=ledger)
    rep = mgr.generate_showback_report("tenant_cb")

    assert rep.direct_cost == Decimal("100.000000")
    assert rep.allocated_shared_cost == Decimal("5.000000")
    assert rep.total_cost == Decimal("105.000000")
