"""
Tests for Degradation Management Module.
"""

from app.reliability.degradation_management import DegradationManager, DegradationStrategy


def test_graceful_degradation_recommendation():
    manager = DegradationManager()

    # Read-only mode when database fails
    res_ro = manager.evaluate_degradation(database_available=False)
    assert res_ro.recommended_strategy == DegradationStrategy.READ_ONLY_MODE
    assert res_ro.auto_traffic_switch_blocked is True

    # Degradation mode when redis fails
    res_deg = manager.evaluate_degradation(redis_available=False)
    assert res_deg.recommended_strategy == DegradationStrategy.GRACEFUL_DEGRADATION
    assert res_deg.auto_traffic_switch_blocked is True
