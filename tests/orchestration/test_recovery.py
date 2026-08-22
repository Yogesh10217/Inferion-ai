"""Unit tests for failure recovery strategy evaluation."""

import pytest
from app.orchestration.recovery import RecoveryManager, RecoveryStrategy


def test_failure_recovery_strategies():
    mgr = RecoveryManager()

    # Attempt 1 -> RETRY
    strat1 = mgr.handle_failure("exec_1", "step_1", "Connection timeout", attempt=1, max_retries=3)
    assert strat1 == RecoveryStrategy.RETRY

    # Attempt 4 (Exceeded max retries) -> COMPENSATE
    strat4 = mgr.handle_failure("exec_1", "step_1", "Connection timeout", attempt=4, max_retries=3)
    assert strat4 == RecoveryStrategy.COMPENSATE
