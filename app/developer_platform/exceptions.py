"""Developer Platform Exception Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class DeveloperPlatformException(AppException):
    """Base exception for all Developer Platform errors."""

    def __init__(
        self,
        message: str,
        code: str = "DEVELOPER_PLATFORM_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class ProjectNotFoundException(DeveloperPlatformException):
    def __init__(self, project_id: str) -> None:
        super().__init__(
            message=f"Developer Project '{project_id}' not found", code="PROJECT_NOT_FOUND", status_code=404
        )


class APIContractBreakingChangeException(DeveloperPlatformException):
    def __init__(self, service_id: str, reason: str) -> None:
        super().__init__(
            message=f"API Contract for '{service_id}' contains breaking changes: {reason}",
            code="API_CONTRACT_BREAKING_CHANGE",
            status_code=409,
        )


class QualityGateViolationException(DeveloperPlatformException):
    def __init__(self, gate_id: str, reason: str) -> None:
        super().__init__(
            message=f"Quality gate '{gate_id}' blocked execution: {reason}",
            code="QUALITY_GATE_VIOLATION",
            status_code=422,
        )


class WorkspaceSecurityViolationException(DeveloperPlatformException):
    def __init__(self, workspace_id: str, reason: str) -> None:
        super().__init__(
            message=f"Workspace '{workspace_id}' security violation: {reason}",
            code="WORKSPACE_SECURITY_VIOLATION",
            status_code=403,
        )


class DependencyRiskViolationException(DeveloperPlatformException):
    def __init__(self, dependency_name: str, risk_level: str) -> None:
        super().__init__(
            message=f"Dependency '{dependency_name}' introduced high vulnerability risk: {risk_level}",
            code="DEPENDENCY_RISK_VIOLATION",
            status_code=422,
        )


class DeveloperNotFoundException(DeveloperPlatformException):
    def __init__(self, developer_id: str) -> None:
        super().__init__(message=f"Developer '{developer_id}' not found", code="DEVELOPER_NOT_FOUND", status_code=404)


class DeveloperPermissionDeniedException(DeveloperPlatformException):
    def __init__(self, reason: str = "Permission denied") -> None:
        super().__init__(message=reason, code="DEVELOPER_PERMISSION_DENIED", status_code=403)


class EventSubscriptionNotFoundException(DeveloperPlatformException):
    def __init__(self, sub_id: str) -> None:
        super().__init__(
            message=f"Event subscription '{sub_id}' not found", code="EVENT_SUBSCRIPTION_NOT_FOUND", status_code=404
        )
