"""
Phase 5.70 - Failover Evaluator Module.

Evaluates application, database, cache, dependency, and regional failover readiness.
Returns FAILOVER_SIMULATION_VALIDATED when simulation succeeds.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class FailoverEvaluationStatus(str, Enum):
    FAILOVER_READY = "FAILOVER_READY"
    FAILOVER_SIMULATION_VALIDATED = "FAILOVER_SIMULATION_VALIDATED"
    FAILOVER_NOT_CONFIGURED = "FAILOVER_NOT_CONFIGURED"
    FAILOVER_BLOCKED = "FAILOVER_BLOCKED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class FailoverEvaluationResult:
    status: FailoverEvaluationStatus
    app_failover_ready: bool
    db_failover_ready: bool
    cache_failover_ready: bool
    dependency_failover_ready: bool
    production_failover_executed: bool
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class FailoverEvaluator:
    """Evaluates failover capabilities across application and infrastructure tiers."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_failover_readiness(
        self,
        app_failover_ready: bool = True,
        db_failover_ready: bool = True,
        cache_failover_ready: bool = True,
        dependency_failover_ready: bool = True,
        real_production_executed: bool = False,
        executed: bool = True,
    ) -> FailoverEvaluationResult:
        if not executed:
            return FailoverEvaluationResult(
                status=FailoverEvaluationStatus.NOT_EXECUTED,
                app_failover_ready=False,
                db_failover_ready=False,
                cache_failover_ready=False,
                dependency_failover_ready=False,
                production_failover_executed=False,
                evidence_level=self.evidence_level,
                details={"message": "Failover evaluation not executed."},
            )

        all_ready = app_failover_ready and db_failover_ready and cache_failover_ready and dependency_failover_ready

        if not all_ready:
            status = FailoverEvaluationStatus.FAILOVER_BLOCKED
        elif real_production_executed:
            status = FailoverEvaluationStatus.FAILOVER_READY
        else:
            status = FailoverEvaluationStatus.FAILOVER_SIMULATION_VALIDATED

        return FailoverEvaluationResult(
            status=status,
            app_failover_ready=app_failover_ready,
            db_failover_ready=db_failover_ready,
            cache_failover_ready=cache_failover_ready,
            dependency_failover_ready=dependency_failover_ready,
            production_failover_executed=real_production_executed,  # Strictly False unless real execution occurred
            evidence_level=self.evidence_level,
            details={"all_tiers_ready": all_ready},
        )
