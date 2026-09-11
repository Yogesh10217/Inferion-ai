"""Custom exceptions for Phase 5.60 Enterprise AI Production Deployment Foundation."""


class DeploymentError(Exception):
    """Base exception for all deployment platform errors."""
    pass


class ConfigurationValidationError(DeploymentError):
    """Raised when runtime or environment configuration fails validation."""
    pass


class UnsafeConfigurationError(ConfigurationValidationError):
    """Raised when unsafe debug flags or fallback secrets are detected in production."""
    pass


class StartupLifecycleError(DeploymentError):
    """Raised when invalid state transitions occur during service startup lifecycle."""
    pass


class ShutdownLifecycleError(DeploymentError):
    """Raised when error or timeout occurs during graceful process shutdown."""
    pass


class DependencyValidationError(DeploymentError):
    """Raised when required infrastructure dependencies fail health probes."""
    pass


class ReleaseValidationBlockedError(DeploymentError):
    """Raised when production release validation checks block deployment."""
    pass


class SecretAccessError(DeploymentError):
    """Raised when secret provider access fails or required secrets are missing."""
    pass


class EnvironmentIsolationError(DeploymentError):
    """Raised when unauthorized cross-environment state or configuration access occurs."""
    pass
