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


class DeploymentDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    NOT_EXECUTED = "NOT_EXECUTED"


class MigrationSafetyStatus(str, Enum):
    MIGRATION_SYSTEM_AVAILABLE = "MIGRATION_SYSTEM_AVAILABLE"
    MIGRATION_SYSTEM_NOT_CONFIGURED = "MIGRATION_SYSTEM_NOT_CONFIGURED"
    MIGRATION_CONFIGURATION_VALIDATED = "MIGRATION_CONFIGURATION_VALIDATED"
    MIGRATION_RUNTIME_NOT_EXECUTED = "MIGRATION_RUNTIME_NOT_EXECUTED"
    MIGRATION_STATE_UNKNOWN = "MIGRATION_STATE_UNKNOWN"


class RollbackTrigger(str, Enum):
    CONFIGURATION_FAILURE = "configuration_failure"
    READINESS_FAILURE = "readiness_failure"
    HEALTH_REGRESSION = "health_regression"
    DEPENDENCY_FAILURE = "dependency_failure"
    CONTAINER_FAILURE = "container_failure"
    MANAGER_REGISTRATION_FAILURE = "manager_registration_failure"
    SECURITY_POLICY_VIOLATION = "security_policy_violation"
    SECRET_EXPOSURE_DETECTION = "secret_exposure_detection"
    DEPLOYMENT_ARTIFACT_MISMATCH = "deployment_artifact_mismatch"


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
    PRODUCTION_CONFIGURATION_READY = "PRODUCTION_CONFIGURATION_READY"
    PRODUCTION_SAFETY_VALIDATED = "PRODUCTION_SAFETY_VALIDATED"
    PRODUCTION_DEPLOYMENT_GATED = "PRODUCTION_DEPLOYMENT_GATED"
    ROLLBACK_STRATEGY_READY = "ROLLBACK_STRATEGY_READY"
    PRODUCTION_SIMULATION_READY = "PRODUCTION_SIMULATION_READY"
    DEPLOYMENT_SIMULATION_EXECUTED = "DEPLOYMENT_SIMULATION_EXECUTED"
    PRODUCTION_SIMULATION_VALIDATED = "PRODUCTION_SIMULATION_VALIDATED"
    ROLLBACK_SIMULATION_EXECUTED = "ROLLBACK_SIMULATION_EXECUTED"
    ROLLBACK_SIMULATION_VALIDATED = "ROLLBACK_SIMULATION_VALIDATED"
    PRODUCTION_READY = "PRODUCTION_READY"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    RUNTIME_BLOCKED = "RUNTIME_BLOCKED"




@dataclass
class DeploymentIdentity:
    application_version: str
    deployment_version: str
    build_identifier: str
    git_revision: str
    environment: str
    image_tag: str = "enterprise-ai-platform:5.61"
    image_digest: str = "NOT_AVAILABLE"

    def canonical_fingerprint(self) -> str:
        import hashlib
        import json
        payload = {
            "application_version": self.application_version,
            "deployment_version": self.deployment_version,
            "build_identifier": self.build_identifier,
            "git_revision": self.git_revision,
            "environment": self.environment,
            "image_tag": self.image_tag,
            "image_digest": self.image_digest,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass
class DeploymentMetadata:
    identity: DeploymentIdentity
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validation_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    build_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class DeploymentState:
    status: str
    identity: DeploymentIdentity
    active_since: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackEvidence:
    trigger: RollbackTrigger
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackPlan:
    trigger: RollbackTrigger
    deployment_identity: DeploymentIdentity
    previous_deployment_reference: str = "NO_PREVIOUS_DEPLOYMENT_REFERENCE"
    required_operator_actions: List[str] = field(default_factory=list)
    automatic_actions: List[str] = field(default_factory=list)
    validation_requirements: List[str] = field(default_factory=list)
    evidence: Optional[RollbackEvidence] = None
    safety_classification: PlatformReadinessClassification = PlatformReadinessClassification.ROLLBACK_STRATEGY_READY
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RollbackState:
    status: str = "ROLLBACK_STRATEGY_READY"
    active_plan: Optional[RollbackPlan] = None
    executed: bool = False


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
    decision: DeploymentDecision = DeploymentDecision.BLOCK
    readiness_classification: PlatformReadinessClassification = PlatformReadinessClassification.RUNTIME_BLOCKED
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)
    migration_safety_status: MigrationSafetyStatus = MigrationSafetyStatus.MIGRATION_RUNTIME_NOT_EXECUTED
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

