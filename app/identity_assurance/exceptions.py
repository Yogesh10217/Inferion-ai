"""Tenant-safe exceptions for Identity Assurance Platform."""


class IdentityAssuranceException(Exception):
    """Base exception for all identity assurance errors."""
    pass


class CrossTenantIdentityAssuranceException(IdentityAssuranceException):
    """Raised when cross-tenant identity access is attempted. Leaks ZERO metadata."""
    def __init__(self, message: str = "Access denied: identity resource not found or access unauthorized.") -> None:
        super().__init__(message)


class IdentityNotFoundException(IdentityAssuranceException):
    """Raised when an identity is not found."""
    pass


class IdentityProfileNotFoundException(IdentityAssuranceException):
    """Raised when an identity profile is not found."""
    pass


class IdentityTrustException(IdentityAssuranceException):
    """Raised when an identity trust assessment fails."""
    pass


class AccessPatternException(IdentityAssuranceException):
    """Raised when an access pattern error occurs."""
    pass


class AuthorizationRiskException(IdentityAssuranceException):
    """Raised when an authorization risk evaluation fails."""
    pass


class PrivilegeRiskException(IdentityAssuranceException):
    """Raised when a privilege risk evaluation fails."""
    pass


class IdentityAnomalyException(IdentityAssuranceException):
    """Raised when an identity anomaly is detected or evaluated."""
    pass


class AccessReviewNotFoundException(IdentityAssuranceException):
    """Raised when an access review is not found."""
    pass


class DelegatedAccessException(IdentityAssuranceException):
    """Raised when delegated access fails or is invalid."""
    pass


class IdentityInvestigationException(IdentityAssuranceException):
    """Raised when an identity investigation error occurs."""
    pass


class IdentityRemediationBlockedException(IdentityAssuranceException):
    """Raised when an identity remediation is blocked."""
    pass


class HighRiskIdentityActionRequiresApprovalException(IdentityAssuranceException):
    """Raised when a high-risk identity action requires human approval."""
    pass


class ImmutableIdentityRecordException(IdentityAssuranceException):
    """Raised when attempting to modify an immutable identity record."""
    pass
