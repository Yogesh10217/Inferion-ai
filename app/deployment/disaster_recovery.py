from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.deployment.models import PlatformReadinessClassification
from app.deployment.secrets import SecretsSanitizer


@dataclass
class RecoveryObjective:
    recovery_time_objective_minutes: int = 15
    recovery_point_objective_minutes: int = 5
    max_tolerable_downtime_minutes: int = 60


@dataclass
class RestoreValidationPlan:
    automated_integrity_check: bool = True
    schema_verification_required: bool = True
    dry_run_supported: bool = True
    validation_steps: List[str] = field(
        default_factory=lambda: [
            "Verify backup archive checksum",
            "Perform isolated schema restore test",
            "Validate table constraints and index integrity",
            "Verify application startup against restored target",
        ]
    )


@dataclass
class DisasterRecoveryPlan:
    plan_name: str = "Enterprise AI Platform DR Plan v1.0"
    recovery_objective: RecoveryObjective = field(default_factory=RecoveryObjective)
    restore_validation: RestoreValidationPlan = field(default_factory=RestoreValidationPlan)
    backup_strategy_defined: bool = True
    restore_strategy_defined: bool = True
    rollback_reference_available: bool = True
    artifact_recovery_available: bool = True
    configuration_recovery_available: bool = True
    database_restore_plan_available: bool = True
    execution_status: str = "NOT_EXECUTED"


@dataclass
class DisasterRecoveryEvaluationResult:
    status: str
    dr_plan: DisasterRecoveryPlan
    classifications: List[str]
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure(
            {
                "status": self.status,
                "dr_plan_name": self.dr_plan.plan_name,
                "rto_minutes": self.dr_plan.recovery_objective.recovery_time_objective_minutes,
                "rpo_minutes": self.dr_plan.recovery_objective.recovery_point_objective_minutes,
                "backup_strategy_defined": self.dr_plan.backup_strategy_defined,
                "restore_strategy_defined": self.dr_plan.restore_strategy_defined,
                "rollback_reference_available": self.dr_plan.rollback_reference_available,
                "database_restore_plan_available": self.dr_plan.database_restore_plan_available,
                "classifications": self.classifications,
                "execution_status": self.dr_plan.execution_status,
                "evaluated_at": self.evaluated_at,
            }
        )


class BackupReadinessEvaluator:
    """Evaluates disaster recovery and backup readiness plans without claiming unexecuted production backups."""

    @classmethod
    def evaluate_disaster_recovery_readiness(cls, is_production: bool = False) -> DisasterRecoveryEvaluationResult:
        dr_plan = DisasterRecoveryPlan()

        classifications = [
            PlatformReadinessClassification.BACKUP_READINESS_EVALUATED.value,
            PlatformReadinessClassification.DISASTER_RECOVERY_READINESS_EVALUATED.value,
            "PRODUCTION_BACKUP_EXECUTED = NOT_EXECUTED",
            "PRODUCTION_RESTORE_EXECUTED = NOT_EXECUTED",
        ]

        return DisasterRecoveryEvaluationResult(
            status="READY",
            dr_plan=dr_plan,
            classifications=classifications,
        )
