"""Domain exceptions for Enterprise Control Plane & Platform Management."""

from typing import Any, Dict, Optional
from app.core.exceptions import AppException


class ControlPlaneException(AppException):
    """Base exception for all control plane domain errors."""

    def __init__(
        self,
        message: str = "A control plane error occurred",
        code: str = "CONTROL_PLANE_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class TenantNotFoundException(ControlPlaneException):
    """Raised when a tenant entity cannot be found."""

    def __init__(self, tenant_id: str) -> None:
        super().__init__(
            message=f"Tenant '{tenant_id}' not found",
            code="TENANT_NOT_FOUND",
            status_code=404,
            details={"tenant_id": tenant_id},
        )


class OrganizationNotFoundException(ControlPlaneException):
    """Raised when an organization entity cannot be found."""

    def __init__(self, organization_id: str) -> None:
        super().__init__(
            message=f"Organization '{organization_id}' not found",
            code="ORGANIZATION_NOT_FOUND",
            status_code=404,
            details={"organization_id": organization_id},
        )


class WorkspaceNotFoundException(ControlPlaneException):
    """Raised when a workspace entity cannot be found."""

    def __init__(self, workspace_id: str) -> None:
        super().__init__(
            message=f"Workspace '{workspace_id}' not found",
            code="WORKSPACE_NOT_FOUND",
            status_code=404,
            details={"workspace_id": workspace_id},
        )


class ResourceNotFoundException(ControlPlaneException):
    """Raised when a managed platform resource cannot be found."""

    def __init__(self, resource_id: str) -> None:
        super().__init__(
            message=f"Platform resource '{resource_id}' not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_id": resource_id},
        )


class ConfigurationException(ControlPlaneException):
    """Raised when configuration validation or scope operation fails."""

    def __init__(self, message: str = "Invalid configuration", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code="CONFIGURATION_ERROR", status_code=400, details=details)


class ConfigurationConflictException(ControlPlaneException):
    """Raised when configuration changes conflict with higher/lower scope policies."""

    def __init__(self, message: str = "Configuration conflict detected", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code="CONFIGURATION_CONFLICT", status_code=409, details=details)


class PolicyViolationException(ControlPlaneException):
    """Raised when an administrative action violates active control plane policy."""

    def __init__(self, message: str = "Control plane policy violation", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code="POLICY_VIOLATION", status_code=403, details=details)


class LifecycleException(ControlPlaneException):
    """Raised when invalid resource state transitions are attempted."""

    def __init__(self, message: str = "Invalid lifecycle state transition", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code="LIFECYCLE_ERROR", status_code=400, details=details)


class AdministrativePermissionDenied(ControlPlaneException):
    """Raised when an identity lacks required administrative rights."""

    def __init__(self, message: str = "Administrative permission denied", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code="ADMIN_PERMISSION_DENIED", status_code=403, details=details)


class ApprovalRequiredException(ControlPlaneException):
    """Raised when high-risk operation requires human or policy approval."""

    def __init__(self, action: str, approval_id: Optional[str] = None) -> None:
        super().__init__(
            message=f"High-risk operation '{action}' requires formal approval",
            code="APPROVAL_REQUIRED",
            status_code=402,
            details={"action": action, "approval_id": approval_id},
        )


class PlatformOperationException(ControlPlaneException):
    """Raised when execution of a control plane operational command fails."""

    def __init__(self, message: str = "Platform operation failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code="PLATFORM_OPERATION_FAILED", status_code=500, details=details)


class ResourceLimitException(ControlPlaneException):
    """Raised when platform resource limits are exceeded."""

    def __init__(self, message: str = "Resource limit exceeded", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code="RESOURCE_LIMIT_EXCEEDED", status_code=429, details=details)
