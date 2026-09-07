"""Tenant-safe exceptions for Operations Assurance Platform."""


class OperationsAssuranceException(Exception):
    """Base exception for all operations assurance errors."""
    pass


class CrossTenantOperationsAssuranceException(OperationsAssuranceException):
    """Raised when cross-tenant operations access is attempted. Leaks ZERO metadata."""
    def __init__(self, message: str = "Access denied: operational resource not found or access unauthorized.") -> None:
        super().__init__(message)


class ServiceNotFoundException(OperationsAssuranceException):
    """Raised when a service is not found."""
    pass


class ServiceHealthNotFoundException(OperationsAssuranceException):
    """Raised when service health assessment is not found."""
    pass


class OperationalIncidentNotFoundException(OperationsAssuranceException):
    """Raised when an operational incident is not found."""
    pass


class OperationalEventNotFoundException(OperationsAssuranceException):
    """Raised when an operational event is not found."""
    pass


class DependencyNotFoundException(OperationsAssuranceException):
    """Raised when a service dependency is not found."""
    pass


class CapacityAssessmentException(OperationsAssuranceException):
    """Raised when a capacity assessment error occurs."""
    pass


class ReliabilityAssessmentException(OperationsAssuranceException):
    """Raised when a reliability assessment error occurs."""
    pass


class OperationalAnomalyException(OperationsAssuranceException):
    """Raised when an operational anomaly error occurs."""
    pass


class RootCauseAnalysisException(OperationsAssuranceException):
    """Raised when root cause analysis fails."""
    pass


class OperationalRecommendationNotFoundException(OperationsAssuranceException):
    """Raised when an operational recommendation is not found."""
    pass


class OperationalPlanNotFoundException(OperationsAssuranceException):
    """Raised when an operational plan is not found."""
    pass


class OperationalRemediationBlockedException(OperationsAssuranceException):
    """Raised when an operational remediation is blocked."""
    pass


class HighRiskOperationalActionRequiresApprovalException(OperationsAssuranceException):
    """Raised when a high-risk operational action requires human approval."""
    pass


class ImmutableOperationalRecordException(OperationsAssuranceException):
    """Raised when attempting to modify an immutable operational record."""
    pass
