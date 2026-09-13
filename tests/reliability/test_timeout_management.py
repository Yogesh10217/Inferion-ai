"""
Tests for Timeout Management Engine Module.
"""

from app.reliability.reliability_models import ReliabilityStatus
from app.reliability.timeout_management import TimeoutConfig, TimeoutManagementEngine


def test_timeout_management_evaluation():
    engine = TimeoutManagementEngine()
    res = engine.evaluate_timeouts(measured_request_sec=0.5, measured_db_sec=0.1)
    assert res.all_within_limits is True
    assert res.status == ReliabilityStatus.HEALTHY


def test_timeout_exceeded():
    engine = TimeoutManagementEngine()
    res = engine.evaluate_timeouts(measured_db_sec=10.0)  # Exceeds 5s threshold
    assert res.all_within_limits is False
    assert res.status == ReliabilityStatus.DEGRADED
