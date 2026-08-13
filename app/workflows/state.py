"""
Workflow & Node State Management Machine
"""

from enum import Enum
from typing import Dict, Set
from app.workflows.exceptions import InvalidStateTransitionError


class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    PAUSED = "PAUSED"
    RESUMING = "RESUMING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class NodeStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


# Valid state transitions for WorkflowStatus
VALID_WORKFLOW_TRANSITIONS: Dict[WorkflowStatus, Set[WorkflowStatus]] = {
    WorkflowStatus.DRAFT: {WorkflowStatus.READY, WorkflowStatus.CANCELLED},
    WorkflowStatus.READY: {WorkflowStatus.PENDING, WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.PENDING: {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.RUNNING: {
        WorkflowStatus.WAITING,
        WorkflowStatus.WAITING_FOR_APPROVAL,
        WorkflowStatus.PAUSED,
        WorkflowStatus.RETRYING,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.WAITING: {WorkflowStatus.RUNNING, WorkflowStatus.RESUMING, WorkflowStatus.CANCELLED, WorkflowStatus.FAILED},
    WorkflowStatus.WAITING_FOR_APPROVAL: {WorkflowStatus.RUNNING, WorkflowStatus.RESUMING, WorkflowStatus.CANCELLED, WorkflowStatus.FAILED},
    WorkflowStatus.PAUSED: {WorkflowStatus.RESUMING, WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.RESUMING: {WorkflowStatus.RUNNING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED},
    WorkflowStatus.RETRYING: {WorkflowStatus.RUNNING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED},
    WorkflowStatus.COMPLETED: set(),
    WorkflowStatus.FAILED: {WorkflowStatus.RETRYING, WorkflowStatus.RESUMING},
    WorkflowStatus.CANCELLED: set(),
}


def validate_workflow_transition(current_state: WorkflowStatus, next_state: WorkflowStatus) -> None:
    """Validates if transitioning from current_state to next_state is allowed."""
    if current_state == next_state:
        return
    allowed = VALID_WORKFLOW_TRANSITIONS.get(current_state, set())
    if next_state not in allowed:
        raise InvalidStateTransitionError(
            f"Invalid workflow state transition from {current_state.value} to {next_state.value}"
        )
