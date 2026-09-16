"""Tenant-safe exceptions for Operations Assurance Platform."""


class OperationsAssuranceException(Exception):
    """Base exception for all operations assurance errors."""


class CrossTenantOperationsAssuranceException(OperationsAssuranceException):
    """Raised when cross-tenant operations access is attempted. Leaks ZERO metadata."""

    def __init__(self, message: str = "Access denied: operational resource not found or access unauthorized.") -> None:
        super().__init__(message)


class ServiceNotFoundException(OperationsAssuranceException):
    """Raised when a service is not found."""


class ServiceHealthNotFoundException(OperationsAssuranceException):
    """Raised when service health assessment is not found."""


class OperationalIncidentNotFoundException(OperationsAssuranceException):
    """Raised when an operational incident is not found."""


class OperationalEventNotFoundException(OperationsAssuranceException):
    """Raised when an operational event is not found."""


class DependencyNotFoundException(OperationsAssuranceException):
    """Raised when a service dependency is not found."""


class CapacityAssessmentException(OperationsAssuranceException):
    """Raised when a capacity assessment error occurs."""


class ReliabilityAssessmentException(OperationsAssuranceException):
    """Raised when a reliability assessment error occurs."""


class OperationalAnomalyException(OperationsAssuranceException):
    """Raised when an operational anomaly error occurs."""


class RootCauseAnalysisException(OperationsAssuranceException):
    """Raised when root cause analysis fails."""


class OperationalRecommendationNotFoundException(OperationsAssuranceException):
    """Raised when an operational recommendation is not found."""


class OperationalPlanNotFoundException(OperationsAssuranceException):
    """Raised when an operational plan is not found."""


class OperationalRemediationBlockedException(OperationsAssuranceException):
    """Raised when an operational remediation is blocked."""


class HighRiskOperationalActionRequiresApprovalException(OperationsAssuranceException):
    """Raised when a high-risk operational action requires human approval."""


class ImmutableOperationalRecordException(OperationsAssuranceException):
    """Raised when attempting to modify an immutable operational record."""
