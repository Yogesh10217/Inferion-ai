"""Domain exceptions for Enterprise AI Platform Operations."""


class PlatformOperationsException(Exception):
    """Base exception for platform operations domain."""
    pass


class ServiceNotFoundException(PlatformOperationsException):
    """Raised when a target operational service is not found."""
    pass


class OperationalSignalException(PlatformOperationsException):
    """Raised when processing an invalid or malformed operational signal."""
    pass


class CorrelationException(PlatformOperationsException):
    """Raised when operational signal correlation fails."""
    pass


class IncidentAnalysisException(PlatformOperationsException):
    """Raised when incident intelligence analysis fails."""
    pass


class ImpactAnalysisException(PlatformOperationsException):
    """Raised when impact analysis calculation fails."""
    pass


class RootCauseAnalysisException(PlatformOperationsException):
    """Raised when root cause diagnosis fails."""
    pass


class RemediationPlanException(PlatformOperationsException):
    """Raised when remediation planning or execution fails."""
    pass


class AutonomousActionDeniedException(PlatformOperationsException):
    """Raised when an autonomous operational action violates policy or boundaries."""
    pass


class RemediationVerificationException(PlatformOperationsException):
    """Raised when post-remediation verification fails."""
    pass


class OperationalPolicyViolationException(PlatformOperationsException):
    """Raised when an operational action violates safety or governance policies."""
    pass
