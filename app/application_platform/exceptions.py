"""Custom exceptions for Enterprise AI Application Platform (Phase 5.22)."""


class ApplicationPlatformException(Exception):
    """Base exception for application platform errors."""
    pass


class ApplicationNotFoundException(ApplicationPlatformException):
    """Raised when an application is not found."""
    pass


class ApplicationVersionNotFoundException(ApplicationPlatformException):
    """Raised when an application version is not found."""
    pass


class ImmutableVersionException(ApplicationPlatformException):
    """Raised when attempting to modify an immutable deployed/active application version."""
    pass


class InvalidLifecycleTransitionException(ApplicationPlatformException):
    """Raised when an invalid lifecycle state transition is requested."""
    pass


class ConsentDeniedException(ApplicationPlatformException):
    """Raised when personalization or experience context violates consent scope."""
    pass


class ExecutionCancelledException(ApplicationPlatformException):
    """Raised when application runtime execution is cancelled by client or deadline."""
    pass


class DeploymentFailedException(ApplicationPlatformException):
    """Raised when an application deployment fails or rolls back."""
    pass


class GovernanceBlockedException(ApplicationPlatformException):
    """Raised when an application execution or action is blocked by governance/safety policy."""
    pass


class SecretRedactionException(ApplicationPlatformException):
    """Raised when secret handling fails during execution or logging."""
    pass


class ResourceBindingException(ApplicationPlatformException):
    """Raised when component composition binding resolution fails."""
    pass
