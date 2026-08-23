"""Unit tests for Intelligence Billing Tracker."""

import pytest
from app.intelligence_platform.billing import IntelligenceBillingTracker


def test_billing_tracker_record_cost():
    tracker = IntelligenceBillingTracker()
    evt = tracker.record_operation_cost("t1", "SIMULATION", amount_usd=0.015, resource_id="res_sim")

    assert evt.event_id.startswith("cost_")
    assert evt.amount_usd == 0.015
