"""
Phase 5.70 - Resilience Evaluator Module.

Evaluates platform resilience across 10 critical resilience vectors.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.reliability.reliability_models import ReliabilityStatus
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


@dataclass
class ResilienceResult:
    resilience_score: float
    status: ReliabilityStatus
    application_resilience: float
    database_resilience: float
    cache_resilience: float
    network_resilience: float
    container_resilience: float
    dependency_resilience: float
    recovery_readiness: float
    rollback_readiness: float
    observability_readiness: float
    security_resilience: float
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class ResilienceEvaluator:
    """Evaluates resilience metrics across application, data, cache, network, container, and security layers."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_resilience(
        self,
        application_resilience: float = 100.0,
        database_resilience: float = 100.0,
        cache_resilience: float = 100.0,
        network_resilience: float = 100.0,
        container_resilience: float = 100.0,
        dependency_resilience: float = 100.0,
        recovery_readiness: float = 100.0,
        rollback_readiness: float = 100.0,
        observability_readiness: float = 100.0,
        security_resilience: float = 100.0,
        executed: bool = True,
    ) -> ResilienceResult:
        if not executed:
            return ResilienceResult(
                resilience_score=0.0,
                status=ReliabilityStatus.NOT_EXECUTED,
                application_resilience=0.0,
                database_resilience=0.0,
                cache_resilience=0.0,
                network_resilience=0.0,
                container_resilience=0.0,
                dependency_resilience=0.0,
                recovery_readiness=0.0,
                rollback_readiness=0.0,
                observability_readiness=0.0,
                security_resilience=0.0,
                evidence_level=self.evidence_level,
                details={"message": "Resilience evaluation not executed."},
            )

        vector_scores = [
            application_resilience,
            database_resilience,
            cache_resilience,
            network_resilience,
            container_resilience,
            dependency_resilience,
            recovery_readiness,
            rollback_readiness,
            observability_readiness,
            security_resilience,
        ]

        clamped = [max(0.0, min(100.0, float(s))) for s in vector_scores]
        count = len(clamped)
        overall_score = round(sum(clamped) / count, 2) if count > 0 else 0.0

        if overall_score >= 90.0:
            status = ReliabilityStatus.HEALTHY
        elif overall_score >= 75.0:
            status = ReliabilityStatus.DEGRADED
        elif overall_score >= 50.0:
            status = ReliabilityStatus.AT_RISK
        else:
            status = ReliabilityStatus.FAILING

        return ResilienceResult(
            resilience_score=overall_score,
            status=status,
            application_resilience=clamped[0],
            database_resilience=clamped[1],
            cache_resilience=clamped[2],
            network_resilience=clamped[3],
            container_resilience=clamped[4],
            dependency_resilience=clamped[5],
            recovery_readiness=clamped[6],
            rollback_readiness=clamped[7],
            observability_readiness=clamped[8],
            security_resilience=clamped[9],
            evidence_level=self.evidence_level,
            details={"vectors_evaluated": count},
        )
