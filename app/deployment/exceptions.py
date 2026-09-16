"""Custom exceptions for Phase 5.60 Enterprise AI Production Deployment Foundation."""


class DeploymentError(Exception):
    """Base exception for all deployment platform errors."""


class ConfigurationValidationError(DeploymentError):
    """Raised when runtime or environment configuration fails validation."""


class UnsafeConfigurationError(ConfigurationValidationError):
    """Raised when unsafe debug flags or fallback secrets are detected in production."""


class StartupLifecycleError(DeploymentError):
    """Raised when invalid state transitions occur during service startup lifecycle."""


class IllegalStateTransitionError(DeploymentError):
    """Raised when illegal state transitions occur in deployment state machines."""


class ShutdownLifecycleError(DeploymentError):
    """Raised when error or timeout occurs during graceful process shutdown."""


class DependencyValidationError(DeploymentError):
    """Raised when required infrastructure dependencies fail health probes."""


class ReleaseValidationBlockedError(DeploymentError):
    """Raised when production release validation checks block deployment."""


class SecretAccessError(DeploymentError):
    """Raised when secret provider access fails or required secrets are missing."""


class EnvironmentIsolationError(DeploymentError):
    """Raised when unauthorized cross-environment state or configuration access occurs."""
