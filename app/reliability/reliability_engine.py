"""
Phase 5.70 - Reliability Engineering Engine Module.

Calculates deterministic reliability scores (0 to 100) and categorizes platform reliability status.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class ReliabilityStatus(str, Enum):
    RELIABLE = "RELIABLE"
    WARNING = "WARNING"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"
    BLOCKED = "BLOCKED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class ReliabilityAssessment:
    dimension: str
    score: float  # 0.0 to 100.0
    status: ReliabilityStatus
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReliabilityResult:
    overall_score: float
    status: ReliabilityStatus
    assessments: List[ReliabilityAssessment]
    evidence_level: ReliabilityEvidenceLevel
    summary: str


class ReliabilityEngineeringEngine:
    """Evaluates comprehensive platform reliability across 10 core dimensions."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_reliability(
        self,
        availability_score: float = 100.0,
        redundancy_score: float = 100.0,
        dependency_resilience_score: float = 100.0,
        recovery_readiness_score: float = 100.0,
        failure_detection_score: float = 100.0,
        incident_response_score: float = 100.0,
        rollback_readiness_score: float = 100.0,
        backup_readiness_score: float = 100.0,
        disaster_recovery_score: float = 100.0,
        business_continuity_score: float = 100.0,
        blocked: bool = False,
        executed: bool = True,
    ) -> ReliabilityResult:
        if not executed:
            return ReliabilityResult(
                overall_score=0.0,
                status=ReliabilityStatus.NOT_EXECUTED,
                assessments=[],
                evidence_level=self.evidence_level,
                summary="Reliability evaluation not executed.",
            )

        if blocked:
            return ReliabilityResult(
                overall_score=0.0,
                status=ReliabilityStatus.BLOCKED,
                assessments=[],
                evidence_level=self.evidence_level,
                summary="Reliability evaluation blocked by critical issue.",
            )

        dimensions = [
            ("availability", availability_score),
            ("redundancy", redundancy_score),
            ("dependency_resilience", dependency_resilience_score),
            ("recovery_readiness", recovery_readiness_score),
            ("failure_detection", failure_detection_score),
            ("incident_response", incident_response_score),
            ("rollback_readiness", rollback_readiness_score),
            ("backup_readiness", backup_readiness_score),
            ("disaster_recovery_readiness", disaster_recovery_score),
            ("business_continuity_readiness", business_continuity_score),
        ]

        assessments: List[ReliabilityAssessment] = []
        total_score = 0.0

        for dim_name, score in dimensions:
            clamped_score = max(0.0, min(100.0, float(score)))
            total_score += clamped_score

            if clamped_score >= 90.0:
                status = ReliabilityStatus.RELIABLE
            elif clamped_score >= 75.0:
                status = ReliabilityStatus.WARNING
            elif clamped_score >= 50.0:
                status = ReliabilityStatus.AT_RISK
            else:
                status = ReliabilityStatus.CRITICAL

            assessments.append(
                ReliabilityAssessment(
                    dimension=dim_name,
                    score=clamped_score,
                    status=status,
                    details={"raw_score": score},
                )
            )

        # Zero division protection
        count = len(dimensions)
        overall_score = round(total_score / count, 2) if count > 0 else 0.0

        if overall_score >= 90.0:
            overall_status = ReliabilityStatus.RELIABLE
        elif overall_score >= 75.0:
            overall_status = ReliabilityStatus.WARNING
        elif overall_score >= 50.0:
            overall_status = ReliabilityStatus.AT_RISK
        else:
            overall_status = ReliabilityStatus.CRITICAL

        return ReliabilityResult(
            overall_score=overall_score,
            status=overall_status,
            assessments=assessments,
            evidence_level=self.evidence_level,
            summary=f"Reliability overall score is {overall_score} ({overall_status.value}).",
        )
