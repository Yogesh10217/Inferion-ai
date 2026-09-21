"""
Tests for Recovery State Machine Module.
"""

import pytest

from app.reliability.recovery_state_machine import (
    IllegalRecoveryTransitionError,
    RecoveryState,
    RecoveryStateMachine,
)


def test_valid_recovery_state_transitions():
    sm = RecoveryStateMachine()
    assert sm.current_state == RecoveryState.NORMAL

    t1 = sm.transition_to(RecoveryState.INCIDENT_DETECTED, reason="Database timeout alert")
    assert sm.current_state == RecoveryState.INCIDENT_DETECTED
    assert t1.evidence_fingerprint.startswith("sha256:")

    sm.transition_to(RecoveryState.RECOVERY_ANALYSIS, reason="Analyzing failure cause")
    assert sm.current_state == RecoveryState.RECOVERY_ANALYSIS
    assert len(sm.history) == 2


def test_illegal_recovery_transition_rejection():
    sm = RecoveryStateMachine()
    with pytest.raises(IllegalRecoveryTransitionError):
        # Direct transition from NORMAL to RECOVERED is illegal
        sm.transition_to(RecoveryState.RECOVERED, reason="Direct jump")
