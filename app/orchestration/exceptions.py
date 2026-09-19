"""Orchestration, Workflow & Business Process Automation Exception Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class OrchestrationException(AppException):
    """Base exception for all Orchestration and Process Automation errors."""

    def __init__(
        self,
        message: str,
        code: str = "ORCHESTRATION_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class WorkflowNotFoundException(OrchestrationException):
    def __init__(self, workflow_id: str) -> None:
        super().__init__(
            message=f"Workflow definition '{workflow_id}' not found", code="WORKFLOW_NOT_FOUND", status_code=404
        )


class WorkflowValidationException(OrchestrationException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Workflow definition validation failed: {reason}",
            code="WORKFLOW_VALIDATION_FAILED",
            status_code=422,
        )


class WorkflowExecutionException(OrchestrationException):
    def __init__(self, execution_id: str, reason: str) -> None:
        super().__init__(
            message=f"Workflow execution '{execution_id}' failed: {reason}",
            code="WORKFLOW_EXECUTION_FAILED",
            status_code=500,
        )


class WorkflowTimeoutException(OrchestrationException):
    def __init__(self, execution_id: str) -> None:
        super().__init__(
            message=f"Workflow execution '{execution_id}' timed out", code="WORKFLOW_TIMEOUT", status_code=408
        )


class WorkflowCancelledException(OrchestrationException):
    def __init__(self, execution_id: str, reason: str = "Cancelled by user") -> None:
        super().__init__(
            message=f"Workflow execution '{execution_id}' was cancelled: {reason}",
            code="WORKFLOW_CANCELLED",
            status_code=400,
        )


class TaskAssignmentException(OrchestrationException):
    def __init__(self, task_id: str, reason: str) -> None:
        super().__init__(
            message=f"Human task assignment failed for '{task_id}': {reason}",
            code="TASK_ASSIGNMENT_FAILED",
            status_code=400,
        )


class CaseNotFoundException(OrchestrationException):
    def __init__(self, case_id: str) -> None:
        super().__init__(message=f"Enterprise case '{case_id}' not found", code="CASE_NOT_FOUND", status_code=404)


class DecisionEvaluationException(OrchestrationException):
    def __init__(self, decision_table_id: str, reason: str) -> None:
        super().__init__(
            message=f"Decision evaluation failed for decision table '{decision_table_id}': {reason}",
            code="DECISION_EVALUATION_FAILED",
            status_code=400,
        )


class CompensationException(OrchestrationException):
    def __init__(self, saga_id: str, step_id: str, reason: str) -> None:
        super().__init__(
            message=f"Saga compensation failed for transaction '{saga_id}' on step '{step_id}': {reason}",
            code="COMPENSATION_FAILED",
            status_code=500,
        )
