"""
Tests for Planning Billing Tracker
"""

from app.planning.planning_billing import PlanningBillingTracker


def test_planning_billing_tracker():
    tracker = PlanningBillingTracker()
    tracker.record_usage("tenant_a", "planning", cost=0.015, tokens_used=500, compute_seconds=1.2)
    tracker.record_usage("tenant_a", "simulation", cost=0.005, tokens_used=200, compute_seconds=0.5)

    summary = tracker.get_billing_summary("tenant_a")
    assert summary["total_cost"] == 0.020
    assert summary["tokens_used"] == 700
    assert summary["operation_counts"]["planning"] == 1
    assert summary["operation_counts"]["simulation"] == 1
