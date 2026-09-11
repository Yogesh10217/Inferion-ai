from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class DeploymentEnvironment(str, Enum):
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEVELOPMENT"
    TEST = "TEST"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class StartupState(str, Enum):
    INITIALIZED = "INITIALIZED"
    CONFIGURATION_VALIDATING = "CONFIGURATION_VALIDATING"
    DEPENDENCY_VALIDATING = "DEPENDENCY_VALIDATING"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    FAILED = "FAILED"


class ShutdownState(str, Enum):
    READY = "READY"
    DRAINING = "DRAINING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class HealthCategory(str, Enum):
    APPLICATION = "APPLICATION"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    MESSAGING = "MESSAGING"
    OBSERVABILITY = "OBSERVABILITY"
    PLATFORM_CONTAINER = "PLATFORM_CONTAINER"
    INTELLIGENCE_MANAGERS = "INTELLIGENCE_MANAGERS"


class DependencyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    OPTIONAL = "OPTIONAL"


class DependencyCategory(str, Enum):
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    MESSAGE_BROKER = "MESSAGE_BROKER"
    OBSERVABILITY = "OBSERVABILITY"
    EXTERNAL_PROVIDER = "EXTERNAL_PROVIDER"


class ArtifactIntegrityStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    VALID = "VALID"
    INVALID = "INVALID"
    UNTRUSTED = "UNTRUSTED"


class DeploymentReleaseStatus(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    BLOCKED = "BLOCKED"


class PlatformReadinessClassification(str, Enum):
    ARCHITECTURALLY_READY = "ARCHITECTURALLY_READY"
    DEPLOYMENT_FOUNDATION_READY = "DEPLOYMENT_FOUNDATION_READY"
    CONTAINER_CONFIGURATION_READY = "CONTAINER_CONFIGURATION_READY"
    STAGING_CONFIGURATION_READY = "STAGING_CONFIGURATION_READY"
    CONTAINER_BUILD_VALIDATED = "CONTAINER_BUILD_VALIDATED"
    CONTAINER_RUNTIME_VALIDATED = "CONTAINER_RUNTIME_VALIDATED"
    STAGING_DEPLOYMENT_EXECUTED = "STAGING_DEPLOYMENT_EXECUTED"
    STAGING_HEALTH_VALIDATED = "STAGING_HEALTH_VALIDATED"
    STAGING_VALIDATED = "STAGING_VALIDATED"
    STAGING_READY = "STAGING_READY"
    PRODUCTION_READY = "PRODUCTION_READY"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    RUNTIME_BLOCKED = "RUNTIME_BLOCKED"



@dataclass
class EnvironmentConfig:
    environment: DeploymentEnvironment
    application_name: str
    application_version: str
    deployment_version: str
    region: str
    instance_id: str
    debug_enabled: bool
    database_url: str
    cache_enabled: bool
    messaging_enabled: bool
    observability_enabled: bool
    log_level: str
    redis_url: str = "redis://localhost:6379/0"
    shutdown_timeout: int = 30
    startup_timeout: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_production(self) -> bool:
        return self.environment == DeploymentEnvironment.PRODUCTION


@dataclass
class ConfigurationValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    configuration_fingerprint: str = ""
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ConfigurationFingerprint:
    fingerprint_hash: str
    sanitized_keys: List[str]
    environment: str
    deployment_version: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class DependencyValidationResult:
    category: DependencyCategory
    name: str
    status: DependencyStatus
    required: bool
    latency_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class HealthCheckResult:
    category: HealthCategory
    name: str
    status: HealthStatus
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SystemHealthReport:
    status: HealthStatus
    environment: str
    version: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checks: List[HealthCheckResult] = field(default_factory=list)


@dataclass
class DiagnosticsReport:
    application_name: str
    application_version: str
    deployment_version: str
    environment: str
    startup_state: StartupState
    uptime_seconds: float
    registered_managers: List[str]
    dependency_health: List[DependencyValidationResult]
    configuration_valid: bool
    observability_active: bool
    readiness_classification: PlatformReadinessClassification
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class DeploymentReleaseValidationResult:
    status: DeploymentReleaseStatus
    readiness_classification: PlatformReadinessClassification
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
