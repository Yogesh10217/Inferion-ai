from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from app.deployment.configuration_fingerprint import ConfigurationFingerprintEngine
from app.deployment.models import ConfigurationValidationResult, EnvironmentConfig
from app.deployment.profiles import DeploymentProfile
from app.deployment.secrets import SecretsSanitizer


class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    NOT_EXECUTED = "NOT_EXECUTED"
    UNAVAILABLE = "UNAVAILABLE"
    MOCK_VALIDATED = "MOCK_VALIDATED"
    DEGRADED = "DEGRADED"


class ValidationType(str, Enum):
    DOCKER_BUILD = "DOCKER_BUILD"
    CONTAINER_RUNTIME = "CONTAINER_RUNTIME"
    HEALTH_PROBE = "HEALTH_PROBE"
    DATABASE_SOCKET = "DATABASE_SOCKET"
    CACHE_SOCKET = "CACHE_SOCKET"
    STAGING_COMPOSE = "STAGING_COMPOSE"
    SHUTDOWN_SIGTERM = "SHUTDOWN_SIGTERM"
    RESTART_SAFETY = "RESTART_SAFETY"
    ENVIRONMENT_SAFETY = "ENVIRONMENT_SAFETY"


@dataclass
class ValidationEvidence:
    validation_name: str
    validation_type: ValidationType
    executed: bool
    status: ValidationStatus
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    command: Optional[str] = None
    exit_code: Optional[int] = None
    duration_ms: float = 0.0
    http_status: Optional[int] = None
    socket_connected: Optional[bool] = None
    sanitized_output: str = ""
    evidence_fingerprint: str = ""

    def __post_init__(self) -> None:
        if not self.evidence_fingerprint:
            self.evidence_fingerprint = self.generate_fingerprint()

    def generate_fingerprint(self) -> str:
        payload = f"{self.validation_name}:{self.validation_type.value}:{self.executed}:{self.status.value}:{self.exit_code}:{self.http_status}:{self.socket_connected}:{self.sanitized_output}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class ValidationRun:
    run_id: str
    environment: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    evidences: List[ValidationEvidence] = field(default_factory=list)
    overall_status: ValidationStatus = ValidationStatus.NOT_EXECUTED

    def add_evidence(self, evidence: ValidationEvidence) -> None:
        self.evidences.append(evidence)
        self.evaluate_overall_status()

    def evaluate_overall_status(self) -> None:
        if not self.evidences:
            self.overall_status = ValidationStatus.NOT_EXECUTED
            return
        statuses = [e.status for e in self.evidences]
        if any(s == ValidationStatus.FAILED for s in statuses):
            self.overall_status = ValidationStatus.FAILED
        elif any(s == ValidationStatus.DEGRADED for s in statuses):
            self.overall_status = ValidationStatus.DEGRADED
        elif all(s in (ValidationStatus.PASSED, ValidationStatus.MOCK_VALIDATED) for s in statuses):
            self.overall_status = ValidationStatus.PASSED
        elif any(s == ValidationStatus.PASSED for s in statuses):
            self.overall_status = ValidationStatus.DEGRADED
        else:
            self.overall_status = ValidationStatus.UNAVAILABLE


class RuntimeValidationEngine:
    """Collects empirical validation evidence for container runtime, deployment, probes, and dependencies."""

    def __init__(self, environment: str = "STAGING") -> None:
        self.run = ValidationRun(
            run_id=f"run-{int(time.time())}",
            environment=environment,
        )

    def record_evidence(
        self,
        name: str,
        val_type: ValidationType,
        executed: bool,
        status: ValidationStatus,
        command: Optional[str] = None,
        exit_code: Optional[int] = None,
        duration_ms: float = 0.0,
        http_status: Optional[int] = None,
        socket_connected: Optional[bool] = None,
        raw_output: str = "",
    ) -> ValidationEvidence:
        sanitized = SecretsSanitizer.sanitize_string(raw_output)
        sanitized_cmd = SecretsSanitizer.sanitize_string(command) if command else None

        evidence = ValidationEvidence(
            validation_name=name,
            validation_type=val_type,
            executed=executed,
            status=status,
            command=sanitized_cmd,
            exit_code=exit_code,
            duration_ms=round(duration_ms, 2),
            http_status=http_status,
            socket_connected=socket_connected,
            sanitized_output=sanitized,
        )
        self.run.add_evidence(evidence)
        return evidence

    def finalize(self) -> ValidationRun:
        self.run.completed_at = datetime.now(timezone.utc).isoformat()
        self.run.evaluate_overall_status()
        return self.run


class RuntimeConfigurationValidator:
    """Validates runtime deployment configuration constraints and safety invariants."""

    URL_REGEX = re.compile(r"^(https?|postgresql|mysql|sqlite|redis|amqp)(\+[a-z0-9_]+)?://", re.IGNORECASE)

    @classmethod
    def validate(cls, config: EnvironmentConfig) -> ConfigurationValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        profile = DeploymentProfile.get_profile(config.environment)

        # Profile validation
        valid_profile, profile_errors = profile.validate_config_against_profile(config)
        if not valid_profile:
            errors.extend(profile_errors)

        # Production safety checks
        if config.is_production():
            if config.debug_enabled:
                errors.append("CRITICAL: Debug mode is explicitly forbidden in PRODUCTION environment")
            if not config.observability_enabled:
                warnings.append("WARNING: Observability is recommended to be enabled in PRODUCTION")
            if "sqlite" in config.database_url.lower():
                warnings.append("WARNING: SQLite database used in PRODUCTION profile; PostgreSQL recommended")

        # URL format checks
        if config.database_url and not cls.URL_REGEX.match(config.database_url):
            errors.append(f"Invalid database_url format: '{config.database_url}'")

        # Service ID and version validation
        if not config.application_name or not config.application_name.strip():
            errors.append("Application name must not be empty")

        if not config.deployment_version or not config.deployment_version.strip():
            errors.append("Deployment version must not be empty")

        # Generate fingerprint
        fp = ConfigurationFingerprintEngine.generate_fingerprint(config)

        return ConfigurationValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            configuration_fingerprint=fp.fingerprint_hash,
        )
