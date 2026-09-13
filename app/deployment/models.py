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
    RELEASE_MANIFEST_VALIDATED = "RELEASE_MANIFEST_VALIDATED"
    PRODUCTION_READINESS_EVALUATED = "PRODUCTION_READINESS_EVALUATED"
    DATABASE_RELEASE_READINESS_VALIDATED = "DATABASE_RELEASE_READINESS_VALIDATED"
    BACKUP_READINESS_EVALUATED = "BACKUP_READINESS_EVALUATED"
    DISASTER_RECOVERY_READINESS_EVALUATED = "DISASTER_RECOVERY_READINESS_EVALUATED"
    OBSERVABILITY_READINESS_VALIDATED = "OBSERVABILITY_READINESS_VALIDATED"
    INFRASTRUCTURE_READINESS_EVALUATED = "INFRASTRUCTURE_READINESS_EVALUATED"
    SECRET_PROVIDER_READINESS_EVALUATED = "SECRET_PROVIDER_READINESS_EVALUATED"
    RELEASE_APPROVAL_WORKFLOW_VALIDATED = "RELEASE_APPROVAL_WORKFLOW_VALIDATED"
    PRODUCTION_RELEASE_CHECKLIST_VALIDATED = "PRODUCTION_RELEASE_CHECKLIST_VALIDATED"
    PRODUCTION_SMOKE_TEST_PLAN_READY = "PRODUCTION_SMOKE_TEST_PLAN_READY"
    RUNTIME_EVIDENCE_AUDITED = "RUNTIME_EVIDENCE_AUDITED"
    GO_NO_GO_DECISION_CERTIFIED = "GO_NO_GO_DECISION_CERTIFIED"
    PRODUCTION_RELEASE_REPORT_GENERATED = "PRODUCTION_RELEASE_REPORT_GENERATED"
    PRODUCTION_RELEASE_APPROVED = "PRODUCTION_RELEASE_APPROVED"
    PRODUCTION_READY = "PRODUCTION_READY"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    RUNTIME_BLOCKED = "RUNTIME_BLOCKED"


class EvidenceLevel(str, Enum):
    STATIC = "STATIC"
    UNIT_TEST = "UNIT_TEST"
    INTEGRATION_TEST = "INTEGRATION_TEST"
    ASGI_RUNTIME = "ASGI_RUNTIME"
    SIMULATION_RUNTIME = "SIMULATION_RUNTIME"
    CONTAINER_RUNTIME = "CONTAINER_RUNTIME"
    INFRASTRUCTURE_RUNTIME = "INFRASTRUCTURE_RUNTIME"
    PRODUCTION_RUNTIME = "PRODUCTION_RUNTIME"


class ProductionReleaseDecision(str, Enum):
    GO = "GO"
    NO_GO = "NO_GO"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    NOT_EXECUTED = "NOT_EXECUTED"


class InfrastructureReadinessStatus(str, Enum):
    INFRASTRUCTURE_CONFIGURATION_READY = "INFRASTRUCTURE_CONFIGURATION_READY"
    INFRASTRUCTURE_SIMULATION_VALIDATED = "INFRASTRUCTURE_SIMULATION_VALIDATED"
    INFRASTRUCTURE_RUNTIME_VALIDATED = "INFRASTRUCTURE_RUNTIME_VALIDATED"
    PRODUCTION_INFRASTRUCTURE_VALIDATED = "PRODUCTION_INFRASTRUCTURE_VALIDATED"




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


# Phase 5.67 — Controlled Production Deployment Execution Models

class ProductionDeploymentState(Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    AUTHORIZED = "AUTHORIZED"
    PREFLIGHT_VALIDATING = "PREFLIGHT_VALIDATING"
    ARTIFACT_VERIFYING = "ARTIFACT_VERIFYING"
    INFRASTRUCTURE_VALIDATING = "INFRASTRUCTURE_VALIDATING"
    DATABASE_VALIDATING = "DATABASE_VALIDATING"
    BACKUP_VALIDATING = "BACKUP_VALIDATING"
    DEPLOYMENT_PREPARING = "DEPLOYMENT_PREPARING"
    DEPLOYMENT_EXECUTING = "DEPLOYMENT_EXECUTING"
    DEPLOYMENT_STARTING = "DEPLOYMENT_STARTING"
    HEALTH_VALIDATING = "HEALTH_VALIDATING"
    SMOKE_TESTING = "SMOKE_TESTING"
    TRAFFIC_VALIDATING = "TRAFFIC_VALIDATING"
    RUNTIME_VALIDATING = "RUNTIME_VALIDATING"
    DEPLOYMENT_VALIDATED = "DEPLOYMENT_VALIDATED"
    FAILED = "FAILED"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    ROLLBACK_EXECUTING = "ROLLBACK_EXECUTING"
    ROLLBACK_VALIDATING = "ROLLBACK_VALIDATING"
    ROLLED_BACK = "ROLLED_BACK"
    VALIDATION_FAILED = "VALIDATION_FAILED"


class DeploymentAuthorizationStatus(Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    PENDING = "PENDING"
    PARTIALLY_APPROVED = "PARTIALLY_APPROVED"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXECUTION_STARTED = "EXECUTION_STARTED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"


class ProgressiveDeliveryStrategy(Enum):
    ALL_AT_ONCE = "ALL_AT_ONCE"
    ROLLING = "ROLLING"
    CANARY = "CANARY"
    BLUE_GREEN = "BLUE_GREEN"
    SIMULATION_ONLY = "SIMULATION_ONLY"


class ProgressiveDeliveryState(Enum):
    NOT_STARTED = "NOT_STARTED"
    PREPARING = "PREPARING"
    CANARY_DEPLOYED = "CANARY_DEPLOYED"
    CANARY_VALIDATING = "CANARY_VALIDATING"
    TRAFFIC_PROMOTING = "TRAFFIC_PROMOTING"
    FULL_DEPLOYMENT = "FULL_DEPLOYMENT"
    FULL_VALIDATING = "FULL_VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    ROLLED_BACK = "ROLLED_BACK"


class TrafficValidationStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    VALIDATING = "VALIDATING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    DEGRADED = "DEGRADED"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"


class RuntimeCertificationStatus(Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"


class DeploymentTargetStatus(Enum):
    TARGET_CONFIGURATION_READY = "TARGET_CONFIGURATION_READY"
    TARGET_CONNECTIVITY_VALIDATED = "TARGET_CONNECTIVITY_VALIDATED"
    TARGET_RUNTIME_VALIDATED = "TARGET_RUNTIME_VALIDATED"
    TARGET_NOT_AVAILABLE = "TARGET_NOT_AVAILABLE"
    TARGET_NOT_EXECUTED = "TARGET_NOT_EXECUTED"


class BackupExecutionStatus(Enum):
    BACKUP_NOT_EXECUTED = "BACKUP_NOT_EXECUTED"
    BACKUP_READY = "BACKUP_READY"
    BACKUP_EXECUTING = "BACKUP_EXECUTING"
    BACKUP_EXECUTED = "BACKUP_EXECUTED"
    BACKUP_VALIDATED = "BACKUP_VALIDATED"
    BACKUP_FAILED = "BACKUP_FAILED"
    RESTORE_NOT_EXECUTED = "RESTORE_NOT_EXECUTED"
    RESTORE_READY = "RESTORE_READY"
    RESTORE_EXECUTING = "RESTORE_EXECUTING"
    RESTORE_EXECUTED = "RESTORE_EXECUTED"
    RESTORE_VALIDATED = "RESTORE_VALIDATED"
    RESTORE_FAILED = "RESTORE_FAILED"


class SmokeTestExecutionStatus(Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    PREPARING = "PREPARING"
    EXECUTING = "EXECUTING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


