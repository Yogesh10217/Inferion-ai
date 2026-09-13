import pytest

from app.operations.incident_state_machine import IllegalStateTransitionError, IncidentState, IncidentStateMachine


def test_incident_state_machine_valid():
    s1 = IncidentStateMachine.transition(IncidentState.NOT_DETECTED, IncidentState.DETECTED)
    assert s1 == IncidentState.DETECTED
    s2 = IncidentStateMachine.transition(s1, IncidentState.TRIAGING)
    assert s2 == IncidentState.TRIAGING


def test_incident_state_machine_illegal_rejected():
    with pytest.raises(IllegalStateTransitionError):
        IncidentStateMachine.transition(IncidentState.NOT_DETECTED, IncidentState.RESOLVED)
