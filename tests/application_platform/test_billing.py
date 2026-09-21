"""Unit tests for Event-Driven Billing & UnifiedCostLedger Attribution."""

from app.application_platform.billing import ApplicationBillingTracker
from app.finops.cost_ledger import CostCategory, UnifiedCostLedger


def test_event_driven_billing_attribution():
    ledger = UnifiedCostLedger()
    tracker = ApplicationBillingTracker(cost_ledger=ledger)

    evt = tracker.record_cost_event(
        tenant_id="tenant_fin",
        application_id="app_copilot",
        application_version="1.0.0",
        execution_id="exec_555",
        category=CostCategory.MODEL_INFERENCE,
        amount_usd=0.015,
    )

    assert evt.amount_usd == 0.015
    assert tracker.get_application_total_cost("tenant_fin", "app_copilot") == 0.015

    # Verify UnifiedCostLedger records the entry
    entries = ledger.list_entries("tenant_fin")
    assert len(entries) > 0
    assert float(entries[0].total_cost) == 0.015
