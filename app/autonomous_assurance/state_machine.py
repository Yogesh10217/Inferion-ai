"""
Reusable Workflow State Machine Subsystem.
Validates allowed workflow state transitions, terminal states, recovery states, and audit trails.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.autonomous_assurance.exceptions import (
    ImmutableAutonomousAssuranceRecordException,
    WorkflowStateTransitionException,
)
from app.autonomous_assurance.workflows import AutonomousWorkflow, WorkflowStatus

# Strict transition graph
VALID_WORKFLOW_TRANSITIONS: Dict[WorkflowStatus, List[WorkflowStatus]] = {
    WorkflowStatus.PROPOSED: [WorkflowStatus.ANALYZING, WorkflowStatus.CANCELLED],
    WorkflowStatus.ANALYZING: [WorkflowStatus.PLANNED, WorkflowStatus.CANCELLED, WorkflowStatus.FAILED],
    WorkflowStatus.PLANNED: [WorkflowStatus.GOVERNANCE_EVALUATED, WorkflowStatus.CANCELLED, WorkflowStatus.FAILED],
    WorkflowStatus.GOVERNANCE_EVALUATED: [
        WorkflowStatus.REQUIRES_APPROVAL,
        WorkflowStatus.APPROVED,
        WorkflowStatus.DENIED,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.COMPLETED,
    ],
    WorkflowStatus.REQUIRES_APPROVAL: [
        WorkflowStatus.APPROVED,
        WorkflowStatus.DENIED,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.COMPLETED,
    ],
    WorkflowStatus.APPROVED: [WorkflowStatus.COORDINATING, WorkflowStatus.CANCELLED, WorkflowStatus.COMPLETED],
    WorkflowStatus.COORDINATING: [
        WorkflowStatus.DELEGATED,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.COMPLETED,
    ],
    WorkflowStatus.DELEGATED: [
        WorkflowStatus.VERIFYING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.COMPLETED,
    ],
    WorkflowStatus.VERIFYING: [
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.RECOVERING,
        WorkflowStatus.COMPENSATING,
    ],
    WorkflowStatus.RECOVERING: [
        WorkflowStatus.COORDINATING,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.COMPENSATING,
    ],
    WorkflowStatus.COMPENSATING: [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.PARTIALLY_COMPLETED],
    WorkflowStatus.COMPLETED: [],  # Terminal state
    WorkflowStatus.PARTIALLY_COMPLETED: [],  # Terminal state
    WorkflowStatus.DENIED: [],  # Terminal state
    WorkflowStatus.FAILED: [WorkflowStatus.RECOVERING, WorkflowStatus.COMPENSATING, WorkflowStatus.COMPLETED],
    WorkflowStatus.CANCELLED: [],  # Terminal state
}


class WorkflowStateMachine:
    """Enforces strict state transitions across workflow lifecycles."""

    def transition(
        self, workflow: AutonomousWorkflow, target_status: WorkflowStatus, reason: Optional[str] = None
    ) -> AutonomousWorkflow:
        if workflow.is_finalized and target_status not in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
            raise ImmutableAutonomousAssuranceRecordException(
                f"Cannot transition finalized workflow '{workflow.workflow_id}'"
            )

        allowed = VALID_WORKFLOW_TRANSITIONS.get(workflow.status, [])
        if target_status not in allowed:
            raise WorkflowStateTransitionException(
                f"Invalid workflow transition from '{workflow.status.value}' to '{target_status.value}' for workflow '{workflow.workflow_id}'."
            )

        workflow.status = target_status
        workflow.updated_at = datetime.now(timezone.utc)
        if reason:
            workflow.metadata.custom["last_transition_reason"] = reason

        if target_status in (
            WorkflowStatus.COMPLETED,
            WorkflowStatus.DENIED,
            WorkflowStatus.CANCELLED,
            WorkflowStatus.PARTIALLY_COMPLETED,
        ):
            workflow.completed_at = datetime.now(timezone.utc)

        return workflow

    def transition_state(
        self, workflow_id_or_obj: Any, tenant_id: str, target_status: WorkflowStatus, reason: Optional[str] = None
    ) -> Any:
        from app.autonomous_assurance.repositories import WorkflowRepository

        repo = WorkflowRepository()
        if hasattr(workflow_id_or_obj, "status"):
            res = self.transition(workflow_id_or_obj, target_status, reason)
            repo.save(res)
            return res

        wf = repo.get(workflow_id_or_obj, tenant_id)
        if not wf:
            wf = AutonomousWorkflow(workflow_id=workflow_id_or_obj, tenant_id=tenant_id, title="Transition Workflow")
        res = self.transition(wf, target_status, reason)
        repo.save(res)
        return res
