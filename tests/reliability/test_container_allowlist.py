"""
Tests for Container Chaos Allowlist Safety.
"""

from app.reliability.reliability_models import ChaosExecutionMode, ChaosFailureType
from app.reliability.failure_injection import FailureInjectionEngine


def test_container_allowlist_enforcement():
    engine = FailureInjectionEngine(allowed_container_ids=["approved-sim-container"])

    # Approved container ID -> succeeds
    res_ok = engine.inject_failure(
        failure_type=ChaosFailureType.CONTAINER_RESTART,
        execution_mode=ChaosExecutionMode.CONTAINER,
        target_container_id="approved-sim-container",
    )
    assert res_ok.failure_detected is True

    # Unapproved container ID -> blocked
    res_blocked = engine.inject_failure(
        failure_type=ChaosFailureType.CONTAINER_RESTART,
        execution_mode=ChaosExecutionMode.CONTAINER,
        target_container_id="random-prod-container",
    )
    assert res_blocked.failure_detected is False
    assert res_blocked.auto_execution_blocked is True
    assert "not in the explicit allowlist" in res_blocked.details.get("error", "")
