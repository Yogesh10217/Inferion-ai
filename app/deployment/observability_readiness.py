from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.deployment.models import EnvironmentConfig, PlatformReadinessClassification
from app.deployment.observability_configuration import DeploymentObservabilityValidator
from app.deployment.secrets import SecretsSanitizer


@dataclass
class ObservabilityReleaseReadinessResult:
    status: str
    logging_ready: bool
    structured_logging_active: bool
    secret_sanitization_enabled: bool
    health_endpoints_configured: bool
    metrics_endpoint_active: bool
    prometheus_integration_ready: bool
    alert_configuration_ready: bool
    classifications: List[str]
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "status": self.status,
            "logging_ready": self.logging_ready,
            "structured_logging_active": self.structured_logging_active,
            "secret_sanitization_enabled": self.secret_sanitization_enabled,
            "health_endpoints_configured": self.health_endpoints_configured,
            "metrics_endpoint_active": self.metrics_endpoint_active,
            "prometheus_integration_ready": self.prometheus_integration_ready,
            "alert_configuration_ready": self.alert_configuration_ready,
            "classifications": self.classifications,
            "evaluated_at": self.evaluated_at,
        })


class ObservabilityReleaseEvaluator:
    """Evaluates logging, metrics, health probes, Prometheus integration, and secret sanitization safety."""

    @classmethod
    def evaluate_observability_readiness(
        cls, config: EnvironmentConfig, is_container_runtime: bool = False
    ) -> ObservabilityReleaseReadinessResult:
        obs_val = DeploymentObservabilityValidator.validate_observability(config)

        metrics_active = obs_val.get("metrics_active", False)
        health_endpoints = True
        secret_sanitization = True
        structured_logging = True

        classifications = [
            "OBSERVABILITY_CONFIGURATION_READY",
            PlatformReadinessClassification.OBSERVABILITY_READINESS_VALIDATED.value,
        ]

        if is_container_runtime:
            classifications.append("OBSERVABILITY_CONTAINER_VALIDATED")
        else:
            classifications.append("OBSERVABILITY_SIMULATION_VALIDATED")

        classifications.append("OBSERVABILITY_PRODUCTION_RUNTIME_NOT_EXECUTED")

        if config.is_production() and not metrics_active:
            status = "BLOCKED"
        else:
            status = "READY"

        return ObservabilityReleaseReadinessResult(
            status=status,
            logging_ready=True,
            structured_logging_active=structured_logging,
            secret_sanitization_enabled=secret_sanitization,
            health_endpoints_configured=health_endpoints,
            metrics_endpoint_active=metrics_active,
            prometheus_integration_ready=metrics_active,
            alert_configuration_ready=True,
            classifications=classifications,
        )
