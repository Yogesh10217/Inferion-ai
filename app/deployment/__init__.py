"""Phase 5.60 — Enterprise AI Production Deployment Foundation.

Provides environment configuration, deployment profiles, containerization validation,
service startup/shutdown lifecycle, runtime configuration validation, health probes,
readiness probes, liveness probes, structured logging, secrets abstraction, dependency validation,
release validation, and deployment metadata management.
"""

from app.deployment.models import (
    DeploymentEnvironment,
    StartupState,
    ShutdownState,
    HealthStatus,
    HealthCategory,
    DependencyStatus,
    DependencyCategory,
    ArtifactIntegrityStatus,
    DeploymentReleaseStatus,
    PlatformReadinessClassification,
    EnvironmentConfig,
    ConfigurationValidationResult,
    ConfigurationFingerprint,
    DependencyValidationResult,
    HealthCheckResult,
    SystemHealthReport,
    DiagnosticsReport,
    DeploymentReleaseValidationResult,
)
from app.deployment.manager import DeploymentPlatformManager

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
