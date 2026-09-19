"""Identity, Access Management & Zero-Trust Security Exceptions Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class IdentitySecurityException(AppException):
    """Base exception for all Identity and Access Management domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "IDENTITY_SECURITY_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class IdentityNotFoundException(IdentitySecurityException):
    def __init__(self, identity_id: str) -> None:
        super().__init__(message=f"Identity '{identity_id}' not found", code="IDENTITY_NOT_FOUND", status_code=404)


class AuthenticationAssuranceException(IdentitySecurityException):
    def __init__(self, required: str, provided: str) -> None:
        super().__init__(
            message=f"Required authentication assurance level '{required}', but provided '{provided}'",
            code="INSUFFICIENT_ASSURANCE",
            status_code=401,
        )


class PrivilegedAccessDeniedException(IdentitySecurityException):
    def __init__(self, role: str, reason: str) -> None:
        super().__init__(
            message=f"Privileged access for role '{role}' denied: {reason}",
            code="PRIVILEGED_ACCESS_DENIED",
            status_code=403,
        )


class SessionRevokedException(IdentitySecurityException):
    def __init__(self, session_id: str, reason: str = "Session revoked due to security event") -> None:
        super().__init__(
            message=f"Session '{session_id}' has been revoked: {reason}", code="SESSION_REVOKED", status_code=401
        )


class AgentBoundaryViolationException(IdentitySecurityException):
    def __init__(self, agent_id: str, requested_action: str) -> None:
        super().__init__(
            message=f"AI Agent '{agent_id}' requested action '{requested_action}' which exceeds delegated permission boundary",
            code="AGENT_BOUNDARY_VIOLATION",
            status_code=403,
        )
