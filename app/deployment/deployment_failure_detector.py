from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import ProductionDeploymentState, RollbackTrigger
from app.deployment.secrets import SecretsSanitizer


@dataclass
class DeploymentFailureRecord:
    failure_type: str
    rollback_trigger: RollbackTrigger
    target_state: ProductionDeploymentState
    rollback_required: bool
    description: str
    evidence_details: Dict[str, Any] = field(default_factory=dict)
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "failure_type": self.failure_type,
            "rollback_trigger": self.rollback_trigger.value,
            "target_state": self.target_state.value,
            "rollback_required": self.rollback_required,
            "description": self.description,
            "evidence_details": self.evidence_details,
            "detected_at": self.detected_at,
        })


class DeploymentFailureDetector:
    """Detects deployment execution failures and maps them to canonical RollbackTriggers and failure states."""

    FAILURE_MAPPING: Dict[str, Dict[str, Any]] = {
        "CONFIGURATION_FAILURE": {
            "trigger": RollbackTrigger.CONFIGURATION_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "DEPLOYMENT_ARTIFACT_MISMATCH": {
            "trigger": RollbackTrigger.DEPLOYMENT_ARTIFACT_MISMATCH,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "INFRASTRUCTURE_FAILURE": {
            "trigger": RollbackTrigger.CONTAINER_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "DATABASE_FAILURE": {
            "trigger": RollbackTrigger.DEPENDENCY_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "BACKUP_FAILURE": {
            "trigger": RollbackTrigger.READINESS_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": False,
        },
        "CONTAINER_FAILURE": {
            "trigger": RollbackTrigger.CONTAINER_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "STARTUP_FAILURE": {
            "trigger": RollbackTrigger.READINESS_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "READINESS_FAILURE": {
            "trigger": RollbackTrigger.READINESS_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "HEALTH_REGRESSION": {
            "trigger": RollbackTrigger.HEALTH_REGRESSION,
            "state": ProductionDeploymentState.ROLLBACK_REQUIRED,
            "rollback_required": True,
        },
        "SECURITY_POLICY_VIOLATION": {
            "trigger": RollbackTrigger.SECURITY_POLICY_VIOLATION,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "SECRET_EXPOSURE_DETECTION": {
            "trigger": RollbackTrigger.SECRET_EXPOSURE_DETECTION,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "TRAFFIC_DEGRADATION": {
            "trigger": RollbackTrigger.HEALTH_REGRESSION,
            "state": ProductionDeploymentState.ROLLBACK_REQUIRED,
            "rollback_required": True,
        },
        "DEPENDENCY_FAILURE": {
            "trigger": RollbackTrigger.DEPENDENCY_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "SMOKE_TEST_FAILURE": {
            "trigger": RollbackTrigger.READINESS_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        },
        "OBSERVABILITY_FAILURE": {
            "trigger": RollbackTrigger.READINESS_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": False,
        },
    }

    @classmethod
    def detect_failure(
        cls, failure_key: str, error_message: str, evidence: Optional[Dict[str, Any]] = None
    ) -> DeploymentFailureRecord:
        mapping = cls.FAILURE_MAPPING.get(failure_key, {
            "trigger": RollbackTrigger.READINESS_FAILURE,
            "state": ProductionDeploymentState.FAILED,
            "rollback_required": True,
        })

        return DeploymentFailureRecord(
            failure_type=failure_key,
            rollback_trigger=mapping["trigger"],
            target_state=mapping["state"],
            rollback_required=mapping["rollback_required"],
            description=error_message,
            evidence_details=evidence or {},
        )
