from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.deployment.container_validation import DockerPreflightValidator
from app.deployment.models import EnvironmentConfig, InfrastructureReadinessStatus, PlatformReadinessClassification
from app.deployment.secrets import SecretsSanitizer


@dataclass
class InfrastructureRequirementItem:
    category: str
    name: str
    status: str  # CONFIGURED, READY, MISSING, BLOCKED, MANUAL_REVIEW_REQUIRED, NOT_EXECUTED
    evidence_level: str
    message: str


@dataclass
class InfrastructureReadinessResult:
    status: str
    overall_classification: InfrastructureReadinessStatus
    requirements: List[InfrastructureRequirementItem]
    classifications: List[str]
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "status": self.status,
            "overall_classification": self.overall_classification.value,
            "requirements": [
                {
                    "category": r.category,
                    "name": r.name,
                    "status": r.status,
                    "evidence_level": r.evidence_level,
                    "message": r.message,
                }
                for r in self.requirements
            ],
            "classifications": self.classifications,
            "evaluated_at": self.evaluated_at,
        })


class InfrastructureReadinessEvaluator:
    """Evaluates infrastructure readiness without automatically provisioning infrastructure."""

    @classmethod
    def evaluate_infrastructure_readiness(
        cls, config: EnvironmentConfig, is_container_runtime: bool = False
    ) -> InfrastructureReadinessResult:
        items: List[InfrastructureRequirementItem] = []

        # 1. Compute & Container Runtime
        docker_info = DockerPreflightValidator.check_docker_daemon()
        if docker_info.get("available"):
            items.append(
                InfrastructureRequirementItem(
                    category="CONTAINER_RUNTIME",
                    name="Host Docker Daemon",
                    status="READY",
                    evidence_level="CONTAINER_RUNTIME",
                    message="Host Docker daemon is active and responsive",
                )
            )
        else:
            items.append(
                InfrastructureRequirementItem(
                    category="CONTAINER_RUNTIME",
                    name="Host Docker Daemon",
                    status="CONFIGURED",
                    evidence_level="SIMULATION_RUNTIME",
                    message="Docker daemon unavailable on host; operating in ASGI simulation mode",
                )
            )

        # 2. Database Infrastructure
        items.append(
            InfrastructureRequirementItem(
                category="DATABASE",
                name="PostgreSQL Connection Configuration",
                status="READY" if config.database_url else "MISSING",
                evidence_level="SIMULATION_RUNTIME" if not is_container_runtime else "CONTAINER_RUNTIME",
                message="Database URL configured",
            )
        )

        # 3. Cache Infrastructure
        items.append(
            InfrastructureRequirementItem(
                category="CACHE",
                name="Redis Cache Configuration",
                status="READY" if config.cache_enabled else "CONFIGURED",
                evidence_level="SIMULATION_RUNTIME" if not is_container_runtime else "CONTAINER_RUNTIME",
                message="Redis cache service configured",
            )
        )

        # 4. Networking, Domain, and TLS Boundaries
        items.append(
            InfrastructureRequirementItem(
                category="NETWORK",
                name="Production Hostname & Domain (DNS)",
                status="NOT_EXECUTED",
                evidence_level="PRODUCTION_RUNTIME",
                message="LIVE_DNS_VALIDATED = NOT_EXECUTED: Production DNS resolution not connected",
            )
        )
        items.append(
            InfrastructureRequirementItem(
                category="SECURITY",
                name="TLS Certificate (HTTPS)",
                status="NOT_EXECUTED",
                evidence_level="PRODUCTION_RUNTIME",
                message="LIVE_TLS_VALIDATED = NOT_EXECUTED: Live SSL/TLS certificate validation not connected",
            )
        )

        # 5. Production Cloud Infrastructure Boundary
        items.append(
            InfrastructureRequirementItem(
                category="CLOUD_INFRASTRUCTURE",
                name="Production Kubernetes / Cloud Cluster",
                status="NOT_EXECUTED",
                evidence_level="PRODUCTION_RUNTIME",
                message="PRODUCTION_INFRASTRUCTURE_VALIDATED = NOT_EXECUTED: Live cloud deployment not executed",
            )
        )

        overall_classification = (
            InfrastructureReadinessStatus.INFRASTRUCTURE_SIMULATION_VALIDATED
            if not is_container_runtime
            else InfrastructureReadinessStatus.INFRASTRUCTURE_RUNTIME_VALIDATED
        )

        classifications = [
            overall_classification.value,
            PlatformReadinessClassification.INFRASTRUCTURE_READINESS_EVALUATED.value,
            "PRODUCTION_INFRASTRUCTURE_VALIDATED = NOT_EXECUTED",
        ]

        has_missing = any(i.status == "MISSING" or i.status == "BLOCKED" for i in items)
        status = "BLOCKED" if has_missing else "READY"

        return InfrastructureReadinessResult(
            status=status,
            overall_classification=overall_classification,
            requirements=items,
            classifications=classifications,
        )
