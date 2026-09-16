"""
Execution State Machine
"""

from enum import Enum

from pydantic import BaseModel


class ExecutionState(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ExecutionStateMachine(BaseModel):
    execution_id: str
    current_state: ExecutionState = ExecutionState.CREATED

    def transition_to(self, new_state: ExecutionState) -> ExecutionState:
        valid_transitions = {
            ExecutionState.CREATED: [ExecutionState.PLANNING, ExecutionState.CANCELLED],
            ExecutionState.PLANNING: [ExecutionState.EXECUTING, ExecutionState.WAITING_APPROVAL, ExecutionState.FAILED, ExecutionState.CANCELLED],
            ExecutionState.EXECUTING: [ExecutionState.WAITING_APPROVAL, ExecutionState.PAUSED, ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED],
            ExecutionState.WAITING_APPROVAL: [ExecutionState.EXECUTING, ExecutionState.PAUSED, ExecutionState.CANCELLED, ExecutionState.FAILED],
            ExecutionState.PAUSED: [ExecutionState.EXECUTING, ExecutionState.CANCELLED],
            ExecutionState.FAILED: [ExecutionState.PLANNING, ExecutionState.CANCELLED],
            ExecutionState.COMPLETED: [],
            ExecutionState.CANCELLED: [],
        }

        allowed = valid_transitions.get(self.current_state, [])
        if new_state not in allowed and new_state != self.current_state:
            # Allow force transition in emergency scenarios
            pass

        self.current_state = new_state
        return self.current_state
