"""Tenant-safe exceptions for Identity Assurance Platform."""


class IdentityAssuranceException(Exception):
    """Base exception for all identity assurance errors."""


class CrossTenantIdentityAssuranceException(IdentityAssuranceException):
    """Raised when cross-tenant identity access is attempted. Leaks ZERO metadata."""

    def __init__(self, message: str = "Access denied: identity resource not found or access unauthorized.") -> None:
        super().__init__(message)


class IdentityNotFoundException(IdentityAssuranceException):
    """Raised when an identity is not found."""


class IdentityProfileNotFoundException(IdentityAssuranceException):
    """Raised when an identity profile is not found."""


class IdentityTrustException(IdentityAssuranceException):
    """Raised when an identity trust assessment fails."""


class AccessPatternException(IdentityAssuranceException):
    """Raised when an access pattern error occurs."""


class AuthorizationRiskException(IdentityAssuranceException):
    """Raised when an authorization risk evaluation fails."""


class PrivilegeRiskException(IdentityAssuranceException):
    """Raised when a privilege risk evaluation fails."""


class IdentityAnomalyException(IdentityAssuranceException):
    """Raised when an identity anomaly is detected or evaluated."""


class AccessReviewNotFoundException(IdentityAssuranceException):
    """Raised when an access review is not found."""


class DelegatedAccessException(IdentityAssuranceException):
    """Raised when delegated access fails or is invalid."""


class IdentityInvestigationException(IdentityAssuranceException):
    """Raised when an identity investigation error occurs."""


class IdentityRemediationBlockedException(IdentityAssuranceException):
    """Raised when an identity remediation is blocked."""


class HighRiskIdentityActionRequiresApprovalException(IdentityAssuranceException):
    """Raised when a high-risk identity action requires human approval."""


class ImmutableIdentityRecordException(IdentityAssuranceException):
    """Raised when attempting to modify an immutable identity record."""
