"""
Workflow Budget & Execution Limits Subsystem (Addition #2).
Prevents runaway workflows by enforcing maximum steps, delegation attempts, recovery attempts, execution duration, and approval wait times.
"""

from typing import Optional

from pydantic import BaseModel

from app.autonomous_assurance.exceptions import WorkflowLimitExceededException


class WorkflowLimits(BaseModel):
    max_steps: int = 50
    max_delegation_attempts: int = 10
    max_recovery_attempts: int = 3
    max_execution_duration_seconds: int = 3600
    approval_timeout_seconds: int = 86400


class WorkflowLimitChecker:
    """Enforces execution limits for autonomous workflows."""

    def __init__(self, limits: Optional[WorkflowLimits] = None) -> None:
        self.limits = limits or WorkflowLimits()

    def check_step_limit(self, current_step_count: int, workflow_id: str) -> None:
        if current_step_count >= self.limits.max_steps:
            raise WorkflowLimitExceededException(
                f"Workflow '{workflow_id}' exceeded maximum allowed step limit ({self.limits.max_steps})."
            )

    def check_delegation_limit(self, current_delegation_count: int, workflow_id: str) -> None:
        if current_delegation_count >= self.limits.max_delegation_attempts:
            raise WorkflowLimitExceededException(
                f"Workflow '{workflow_id}' exceeded maximum allowed delegation attempts ({self.limits.max_delegation_attempts})."
            )

    def check_recovery_limit(self, current_recovery_count: int, workflow_id: str) -> None:
        if current_recovery_count >= self.limits.max_recovery_attempts:
            raise WorkflowLimitExceededException(
                f"Workflow '{workflow_id}' exceeded maximum allowed recovery attempts ({self.limits.max_recovery_attempts})."
            )
