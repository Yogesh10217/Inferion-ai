"""
Tests for Execution State Machine
"""

from app.autonomy.state_machine import ExecutionState, ExecutionStateMachine


def test_state_machine_transitions():
    sm = ExecutionStateMachine(execution_id="exec_test")
    assert sm.current_state == ExecutionState.CREATED

    sm.transition_to(ExecutionState.PLANNING)
    assert sm.current_state == ExecutionState.PLANNING

    sm.transition_to(ExecutionState.EXECUTING)
    assert sm.current_state == ExecutionState.EXECUTING

    sm.transition_to(ExecutionState.COMPLETED)
    assert sm.current_state == ExecutionState.COMPLETED
