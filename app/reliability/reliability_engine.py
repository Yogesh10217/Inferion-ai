"""
Phase 5.70 - Reliability Engineering Engine Module.

Calculates deterministic reliability scores (0 to 100) across 10 explicit dimensions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.reliability.reliability_models import ReliabilityStatus
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


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


class ReliabilityEngine:
    """Evaluates comprehensive platform reliability across 10 explicit core dimensions."""

    EXPLICIT_DIMENSIONS = [
        "application_resilience",
        "database_resilience",
        "cache_resilience",
        "network_resilience",
        "dependency_resilience",
        "container_resilience",
        "recovery_capability",
        "failover_readiness",
        "observability_and_detection",
        "security_dependency_resilience",
    ]

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_reliability(
        self,
        application_resilience_score: float = 100.0,
        database_resilience_score: float = 100.0,
        cache_resilience_score: float = 100.0,
        network_resilience_score: float = 100.0,
        dependency_resilience_score: float = 100.0,
        container_resilience_score: float = 100.0,
        recovery_capability_score: float = 100.0,
        failover_readiness_score: float = 100.0,
        observability_detection_score: float = 100.0,
        security_dependency_score: float = 100.0,
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
                summary="Reliability evaluation blocked by critical failure or audit tampering.",
            )

        dimensions = [
            ("application_resilience", application_resilience_score),
            ("database_resilience", database_resilience_score),
            ("cache_resilience", cache_resilience_score),
            ("network_resilience", network_resilience_score),
            ("dependency_resilience", dependency_resilience_score),
            ("container_resilience", container_resilience_score),
            ("recovery_capability", recovery_capability_score),
            ("failover_readiness", failover_readiness_score),
            ("observability_and_detection", observability_detection_score),
            ("security_dependency_resilience", security_dependency_score),
        ]

        assessments: List[ReliabilityAssessment] = []
        total_score = 0.0

        for dim_name, score in dimensions:
            clamped_score = max(0.0, min(100.0, float(score)))
            total_score += clamped_score

            if clamped_score >= 90.0:
                status = ReliabilityStatus.HEALTHY
            elif clamped_score >= 75.0:
                status = ReliabilityStatus.DEGRADED
            elif clamped_score >= 50.0:
                status = ReliabilityStatus.AT_RISK
            else:
                status = ReliabilityStatus.FAILING

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
            overall_status = ReliabilityStatus.HEALTHY
        elif overall_score >= 75.0:
            overall_status = ReliabilityStatus.DEGRADED
        elif overall_score >= 50.0:
            overall_status = ReliabilityStatus.AT_RISK
        else:
            overall_status = ReliabilityStatus.FAILING

        return ReliabilityResult(
            overall_score=overall_score,
            status=overall_status,
            assessments=assessments,
            evidence_level=self.evidence_level,
            summary=f"Reliability overall score is {overall_score} ({overall_status.value}).",
        )


# Backward compatibility alias
ReliabilityEngineeringEngine = ReliabilityEngine
