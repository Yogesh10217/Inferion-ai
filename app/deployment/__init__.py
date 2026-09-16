"""Phase 5.60 — Enterprise AI Production Deployment Foundation.

Provides environment configuration, deployment profiles, containerization validation,
service startup/shutdown lifecycle, runtime configuration validation, health probes,
readiness probes, liveness probes, structured logging, secrets abstraction, dependency validation,
release validation, and deployment metadata management.
"""

from app.deployment.manager import DeploymentPlatformManager
from app.deployment.models import (
    ArtifactIntegrityStatus,
    ConfigurationFingerprint,
    ConfigurationValidationResult,
    DependencyCategory,
    DependencyStatus,
    DependencyValidationResult,
    DeploymentEnvironment,
    DeploymentReleaseStatus,
    DeploymentReleaseValidationResult,
    DiagnosticsReport,
    EnvironmentConfig,
    HealthCategory,
    HealthCheckResult,
    HealthStatus,
    PlatformReadinessClassification,
    ShutdownState,
    StartupState,
    SystemHealthReport,
)

__all__ = [
    "DeploymentEnvironment",
    "StartupState",
    "ShutdownState",
    "HealthStatus",
    "HealthCategory",
    "DependencyStatus",
    "DependencyCategory",
    "ArtifactIntegrityStatus",
    "DeploymentReleaseStatus",
    "PlatformReadinessClassification",
    "EnvironmentConfig",
    "ConfigurationValidationResult",
    "ConfigurationFingerprint",
    "DependencyValidationResult",
    "HealthCheckResult",
    "SystemHealthReport",
    "DiagnosticsReport",
    "DeploymentReleaseValidationResult",
    "DeploymentPlatformManager",
]
