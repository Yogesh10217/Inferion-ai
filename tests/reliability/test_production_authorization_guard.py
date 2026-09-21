"""
Tests for Production Authorization Guard (7 mandatory conditions).
"""

from app.reliability.failure_injection import FailureInjectionEngine
from app.reliability.reliability_models import ChaosExecutionMode, ChaosFailureType


def test_production_authorization_guard_requires_all_seven_conditions():
    engine = FailureInjectionEngine()

    incomplete_auth = {
        "target_configured": True,
        "human_authorized": True,
        "release_authorized": True,
        "target_identity_verified": True,
        "artifact_digest_verified": True,
        "experiment_authorized": True,
        # Missing auto_execution_blocked_overridden
    }

    res_blocked = engine.inject_failure(
        failure_type=ChaosFailureType.DATABASE_UNAVAILABLE,
        execution_mode=ChaosExecutionMode.PRODUCTION,
        production_auth_params=incomplete_auth,
    )

    assert res_blocked.failure_detected is False
    assert res_blocked.auto_execution_blocked is True
    assert res_blocked.details.get("status") == "PRODUCTION_CHAOS_EXECUTION = NOT_EXECUTED"

    # All 7 conditions met
    complete_auth = dict(incomplete_auth, auto_execution_blocked_overridden=True)
    res_allowed = engine.inject_failure(
        failure_type=ChaosFailureType.DATABASE_UNAVAILABLE,
        execution_mode=ChaosExecutionMode.PRODUCTION,
        production_auth_params=complete_auth,
    )
    assert res_allowed.failure_detected is True
