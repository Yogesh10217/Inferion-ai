from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from app.deployment.models import PlatformReadinessClassification, RuntimeCertificationStatus
from app.deployment.secrets import SecretsSanitizer


@dataclass
class ProductionRuntimeCertification:
    deployment_id: str
    artifact_digest: str
    environment: str
    deployment_status: str
    runtime_status: RuntimeCertificationStatus
    evidence_level: str
    validation_results: Dict[str, Any]
    evidence_fingerprint: str
    truthfulness_status: str
    issued_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure(
            {
                "deployment_id": self.deployment_id,
                "artifact_digest": self.artifact_digest,
                "environment": self.environment,
                "deployment_status": self.deployment_status,
                "runtime_status": self.runtime_status.value,
                "evidence_level": self.evidence_level,
                "validation_results": self.validation_results,
                "evidence_fingerprint": self.evidence_fingerprint,
                "truthfulness_status": self.truthfulness_status,
                "issued_at": self.issued_at,
            }
        )


class ProductionRuntimeCertificationEngine:
    """Issues empirical runtime certifications based strictly on verified execution evidence."""

    @classmethod
    def certify_runtime(
        cls,
        deployment_id: str,
        artifact_digest: str,
        environment: str,
        adapter_type: str,
        execution_evidence: Dict[str, Any],
        health_validated: bool,
        smoke_tests_passed: bool,
        traffic_validated: bool,
    ) -> ProductionRuntimeCertification:
        env_norm = environment.upper()

        if adapter_type == "SIMULATION":
            evidence_level = "SIMULATION_RUNTIME"
            truthfulness = "SIMULATION_RUNTIME_VALIDATED"
            cert_status = (
                RuntimeCertificationStatus.VALIDATED if health_validated else RuntimeCertificationStatus.FAILED
            )
        elif adapter_type == "CONTAINER":
            evidence_level = "CONTAINER_RUNTIME"
            truthfulness = PlatformReadinessClassification.CONTAINER_RUNTIME_VALIDATED.value
            cert_status = (
                RuntimeCertificationStatus.VALIDATED
                if (health_validated and smoke_tests_passed)
                else RuntimeCertificationStatus.FAILED
            )
        elif adapter_type == "PRODUCTION":
            has_real_prod = execution_evidence.get("has_real_production_infrastructure", False)
            if not has_real_prod:
                evidence_level = "INFRASTRUCTURE_RUNTIME"
                truthfulness = "NOT_EXECUTED"
                cert_status = RuntimeCertificationStatus.NOT_EXECUTED
            else:
                if health_validated and smoke_tests_passed and traffic_validated:
                    evidence_level = "PRODUCTION_RUNTIME"
                    truthfulness = "LIVE_PRODUCTION_VALIDATED"
                    cert_status = RuntimeCertificationStatus.VALIDATED
                else:
                    evidence_level = "PRODUCTION_RUNTIME"
                    truthfulness = "PRODUCTION_EXECUTION_FAILED"
                    cert_status = RuntimeCertificationStatus.FAILED
        else:
            evidence_level = "STATIC"
            truthfulness = "NOT_EXECUTED"
            cert_status = RuntimeCertificationStatus.NOT_EXECUTED

        validation_results = {
            "adapter_type": adapter_type,
            "health_validated": health_validated,
            "smoke_tests_passed": smoke_tests_passed,
            "traffic_validated": traffic_validated,
            "evidence": execution_evidence,
        }

        canonical_str = json.dumps(
            {
                "dep_id": deployment_id,
                "digest": artifact_digest,
                "env": env_norm,
                "truthfulness": truthfulness,
                "results": SecretsSanitizer.sanitize_structure(validation_results),
            },
            sort_keys=True,
        )
        fp = f"sha256:{hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()}"

        return ProductionRuntimeCertification(
            deployment_id=deployment_id,
            artifact_digest=artifact_digest,
            environment=env_norm,
            deployment_status="VALIDATED" if cert_status == RuntimeCertificationStatus.VALIDATED else cert_status.value,
            runtime_status=cert_status,
            evidence_level=evidence_level,
            validation_results=SecretsSanitizer.sanitize_structure(validation_results),
            evidence_fingerprint=fp,
            truthfulness_status=truthfulness,
        )
