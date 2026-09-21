"""Unit tests for exception recovery strategies."""

from app.orchestration.recovery import RecoveryManager, RecoveryStrategy


def test_failure_recovery_max_retry_fallback():
    mgr = RecoveryManager()
    strat = mgr.handle_failure("exec_f", "step_x", "Fatal error", attempt=5, max_retries=3)

    assert strat == RecoveryStrategy.COMPENSATE
