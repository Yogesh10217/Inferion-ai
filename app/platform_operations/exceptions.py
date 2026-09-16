"""Domain exceptions for Enterprise AI Platform Operations."""


class PlatformOperationsException(Exception):
    """Base exception for platform operations domain."""


class ServiceNotFoundException(PlatformOperationsException):
    """Raised when a target operational service is not found."""


class OperationalSignalException(PlatformOperationsException):
    """Raised when processing an invalid or malformed operational signal."""


class CorrelationException(PlatformOperationsException):
    """Raised when operational signal correlation fails."""


class IncidentAnalysisException(PlatformOperationsException):
    """Raised when incident intelligence analysis fails."""


class ImpactAnalysisException(PlatformOperationsException):
    """Raised when impact analysis calculation fails."""


class RootCauseAnalysisException(PlatformOperationsException):
    """Raised when root cause diagnosis fails."""


class RemediationPlanException(PlatformOperationsException):
    """Raised when remediation planning or execution fails."""


class AutonomousActionDeniedException(PlatformOperationsException):
    """Raised when an autonomous operational action violates policy or boundaries."""


class RemediationVerificationException(PlatformOperationsException):
    """Raised when post-remediation verification fails."""


class OperationalPolicyViolationException(PlatformOperationsException):
    """Raised when an operational action violates safety or governance policies."""
