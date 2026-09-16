"""Operations Domain Exceptions Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class OperationsException(AppException):
    """Base exception for all Operations domain errors."""

    def __init__(self, message: str, code: str = "OPERATIONS_ERROR", status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class SLOBreachException(OperationsException):
    def __init__(self, slo_name: str, target: float, current: float) -> None:
        super().__init__(
            message=f"SLO '{slo_name}' breached: Target = {target}%, Current = {current}%",
            code="SLO_BREACH",
            status_code=429,
        )


class RemediationFailedException(OperationsException):
    def __init__(self, plan_id: str, reason: str) -> None:
        super().__init__(message=f"Remediation plan '{plan_id}' failed: {reason}", code="REMEDIATION_FAILED", status_code=422)


class RunbookExecutionException(OperationsException):
    def __init__(self, runbook_id: str, reason: str) -> None:
        super().__init__(message=f"Runbook '{runbook_id}' execution failed: {reason}", code="RUNBOOK_FAILED", status_code=422)


class IncidentNotFoundException(OperationsException):
    def __init__(self, incident_id: str) -> None:
        super().__init__(message=f"Incident '{incident_id}' not found", code="INCIDENT_NOT_FOUND", status_code=404)
