"""
Tests for Chaos State Machine Module.
"""

import pytest

from app.reliability.chaos_state_machine import ChaosState, ChaosStateMachine, IllegalStateTransitionError


def test_valid_chaos_state_machine_lifecycle():
    sm = ChaosStateMachine(experiment_id="exp-01")
    assert sm.current_state == ChaosState.CREATED

    sm.transition_to(ChaosState.VALIDATING, reason="Validating params")
    sm.transition_to(ChaosState.AUTHORIZED, reason="Operator approved")
    sm.transition_to(ChaosState.RUNNING, reason="Starting experiment")
    sm.transition_to(ChaosState.FAILURE_INJECTED, reason="Failure injected")
    sm.transition_to(ChaosState.OBSERVING, reason="Observing system")
    sm.transition_to(ChaosState.RECOVERING, reason="Triggering recovery")
    sm.transition_to(ChaosState.VALIDATING_RECOVERY, reason="Validating probes")
    sm.transition_to(ChaosState.COMPLETED, reason="Completed successfully")

    assert sm.current_state == ChaosState.COMPLETED
    assert len(sm.history) == 8


def test_illegal_chaos_state_transition():
    sm = ChaosStateMachine(experiment_id="exp-02")
    with pytest.raises(IllegalStateTransitionError):
        # Cannot jump from CREATED directly to COMPLETED
        sm.transition_to(ChaosState.COMPLETED, reason="Illegal jump")
