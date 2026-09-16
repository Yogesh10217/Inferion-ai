"""
Phase 5.70 - Backup Recovery Module.

Evaluates backup configuration, retention policy, backup integrity, restore readiness, and RPO compliance.
Preserves Truthfulness Boundary: Backup readiness does NOT imply PRODUCTION_BACKUP_EXECUTED.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class BackupClassification(str, Enum):
    READY = "READY"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class BackupRecoveryResult:
    classification: BackupClassification
    backup_configured: bool
    retention_policy_valid: bool
    integrity_verified: bool
    restore_ready: bool
    rpo_compliant: bool
    production_backup_executed: bool  # Strict truthfulness boundary flag
    details: Dict[str, Any]
    evidence_level: ReliabilityEvidenceLevel


class BackupRecoveryEvaluator:
    """Evaluates backup and recovery configuration readiness without claiming unexecuted production backups."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_backup_readiness(
        self,
        backup_configured: bool = True,
        retention_days: int = 30,
        integrity_verified: bool = True,
        restore_ready: bool = True,
        estimated_rpo_minutes: float = 5.0,
        target_rpo_minutes: float = 5.0,
        real_production_executed: bool = False,
        executed: bool = True,
    ) -> BackupRecoveryResult:
        if not executed:
            return BackupRecoveryResult(
                classification=BackupClassification.NOT_EXECUTED,
                backup_configured=False,
                retention_policy_valid=False,
                integrity_verified=False,
                restore_ready=False,
                rpo_compliant=False,
                production_backup_executed=False,
                details={"message": "Backup recovery evaluation not executed."},
                evidence_level=self.evidence_level,
            )

        retention_valid = retention_days >= 7
        rpo_compliant = estimated_rpo_minutes <= target_rpo_minutes

        if not backup_configured or not integrity_verified or not restore_ready:
            classification = BackupClassification.BLOCKED
        elif not retention_valid or not rpo_compliant:
            classification = BackupClassification.WARNING
        else:
            classification = BackupClassification.READY

        return BackupRecoveryResult(
            classification=classification,
            backup_configured=backup_configured,
            retention_policy_valid=retention_valid,
            integrity_verified=integrity_verified,
            restore_ready=restore_ready,
            rpo_compliant=rpo_compliant,
            production_backup_executed=real_production_executed,  # Strictly False unless real execution occurred
            details={
                "retention_days": retention_days,
                "estimated_rpo_minutes": estimated_rpo_minutes,
                "target_rpo_minutes": target_rpo_minutes,
            },
            evidence_level=self.evidence_level,
        )
