"""Domain exception hierarchy for Enterprise Security & Identity."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class SecurityException(AppException):
    """Base exception for all security domain errors."""

    def __init__(
        self,
        message: str = "A security error occurred",
        code: str = "SECURITY_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class AuthenticationError(SecurityException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTHENTICATION_ERROR",
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class AuthorizationError(SecurityException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Authorization failed",
        code: str = "AUTHORIZATION_ERROR",
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class InvalidTokenError(AuthenticationError):
    """Raised when a provided token is invalid."""

    def __init__(
        self,
        message: str = "Invalid authentication token",
        code: str = "INVALID_TOKEN",
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class ExpiredTokenError(AuthenticationError):
    """Raised when an authentication token has expired."""

    def __init__(
        self,
        message: str = "Authentication token has expired",
        code: str = "EXPIRED_TOKEN",
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class InvalidAPIKeyError(AuthenticationError):
    """Raised when an API key is invalid, revoked, or expired."""

    def __init__(
        self,
        message: str = "Invalid or revoked API key",
        code: str = "INVALID_API_KEY",
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class PermissionDeniedError(AuthorizationError):
    """Raised when an identity lacks required permissions or scopes."""

    def __init__(
        self,
        message: str = "Permission denied for action",
        code: str = "PERMISSION_DENIED",
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class TenantAccessDeniedError(AuthorizationError):
    """Raised when cross-tenant resource access is attempted."""

    def __init__(
        self,
        message: str = "Access to tenant resource denied",
        code: str = "TENANT_ACCESS_DENIED",
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class SecretAccessDeniedError(AuthorizationError):
    """Raised when access to a secret is denied."""

    def __init__(
        self,
        message: str = "Access to secret denied",
        code: str = "SECRET_ACCESS_DENIED",
        status_code: int = 403,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class RateLimitExceededError(SecurityException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "RATE_LIMIT_EXCEEDED",
        status_code: int = 429,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class QuotaExceededError(SecurityException):
    """Raised when a usage quota is exceeded."""

    def __init__(
        self,
        message: str = "Usage quota exceeded",
        code: str = "QUOTA_EXCEEDED",
        status_code: int = 429,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class SecurityPolicyViolation(SecurityException):
    """Raised when a request violates configured security policy."""

    def __init__(
        self,
        message: str = "Security policy violation",
        code: str = "SECURITY_POLICY_VIOLATION",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)
