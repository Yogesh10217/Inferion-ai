"""
Phase 5.70 - Recovery Objectives Module.

Evaluates RTO, RPO, MTTD, MTTA, and MTTR compliance.
Preserves Truthfulness Boundary: Objectives are claimed as met only when empirical evidence exists.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


@dataclass
class RecoveryObjective:
    rto_target_seconds: float = 900.0  # 15 minutes max downtime
    rpo_target_seconds: float = 300.0  # 5 minutes max data loss
    mttd_target_seconds: float = 60.0   # 1 minute to detect
    mtta_target_seconds: float = 300.0  # 5 minutes to acknowledge
    mttr_target_seconds: float = 900.0  # 15 minutes to recover


@dataclass
class RecoveryObjectiveResult:
    rto_compliant: bool
    rpo_compliant: bool
    mttd_compliant: bool
    mtta_compliant: bool
    mttr_compliant: bool
    overall_compliant: bool
    empirical_evidence_present: bool
    details: Dict[str, Any]
    evidence_level: ReliabilityEvidenceLevel


class RecoveryObjectivesEvaluator:
    """Evaluates recovery metrics against target thresholds (RTO <= 15m, RPO <= 5m)."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_objectives(
        self,
        targets: Optional[RecoveryObjective] = None,
        measured_rto_seconds: Optional[float] = None,
        measured_rpo_seconds: Optional[float] = None,
        measured_mttd_seconds: Optional[float] = None,
        measured_mtta_seconds: Optional[float] = None,
        measured_mttr_seconds: Optional[float] = None,
        empirical_evidence_present: bool = True,
        executed: bool = True,
    ) -> RecoveryObjectiveResult:
        if targets is None:
            targets = RecoveryObjective()

        if not executed:
            return RecoveryObjectiveResult(
                rto_compliant=False,
                rpo_compliant=False,
                mttd_compliant=False,
                mtta_compliant=False,
                mttr_compliant=False,
                overall_compliant=False,
                empirical_evidence_present=False,
                details={"message": "Recovery objectives evaluation not executed."},
                evidence_level=self.evidence_level,
            )

        rto_ok = measured_rto_seconds is not None and measured_rto_seconds <= targets.rto_target_seconds
        rpo_ok = measured_rpo_seconds is not None and measured_rpo_seconds <= targets.rpo_target_seconds
        mttd_ok = measured_mttd_seconds is not None and measured_mttd_seconds <= targets.mttd_target_seconds
        mtta_ok = measured_mtta_seconds is not None and measured_mtta_seconds <= targets.mtta_target_seconds
        mttr_ok = measured_mttr_seconds is not None and measured_mttr_seconds <= targets.mttr_target_seconds

        overall_ok = rto_ok and rpo_ok and mttd_ok and mtta_ok and mttr_ok and empirical_evidence_present

        return RecoveryObjectiveResult(
            rto_compliant=rto_ok,
            rpo_compliant=rpo_ok,
            mttd_compliant=mttd_ok,
            mtta_compliant=mtta_ok,
            mttr_compliant=mttr_ok,
            overall_compliant=overall_ok,
            empirical_evidence_present=empirical_evidence_present,
            details={
                "measured_rto": measured_rto_seconds,
                "target_rto": targets.rto_target_seconds,
                "measured_rpo": measured_rpo_seconds,
                "target_rpo": targets.rpo_target_seconds,
            },
            evidence_level=self.evidence_level,
        )
