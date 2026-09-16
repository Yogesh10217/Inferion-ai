"""Custom exceptions for Enterprise AI Application Platform (Phase 5.22)."""


class ApplicationPlatformException(Exception):
    """Base exception for application platform errors."""


class ApplicationNotFoundException(ApplicationPlatformException):
    """Raised when an application is not found."""


class ApplicationVersionNotFoundException(ApplicationPlatformException):
    """Raised when an application version is not found."""


class ImmutableVersionException(ApplicationPlatformException):
    """Raised when attempting to modify an immutable deployed/active application version."""


class InvalidLifecycleTransitionException(ApplicationPlatformException):
    """Raised when an invalid lifecycle state transition is requested."""


class ConsentDeniedException(ApplicationPlatformException):
    """Raised when personalization or experience context violates consent scope."""


class ExecutionCancelledException(ApplicationPlatformException):
    """Raised when application runtime execution is cancelled by client or deadline."""


class DeploymentFailedException(ApplicationPlatformException):
    """Raised when an application deployment fails or rolls back."""


class GovernanceBlockedException(ApplicationPlatformException):
    """Raised when an application execution or action is blocked by governance/safety policy."""


class SecretRedactionException(ApplicationPlatformException):
    """Raised when secret handling fails during execution or logging."""


class ResourceBindingException(ApplicationPlatformException):
    """Raised when component composition binding resolution fails."""
