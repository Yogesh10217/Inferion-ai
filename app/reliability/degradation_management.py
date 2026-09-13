"""
Phase 5.70 - Degradation Management Module.

Evaluates and recommends graceful degradation strategies under degraded platform conditions.
Does NOT automatically modify production traffic (recommendations only).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class DegradationStrategy(str, Enum):
    FULL_SERVICE = "FULL_SERVICE"
    GRACEFUL_DEGRADATION = "GRACEFUL_DEGRADATION"
    READ_ONLY_MODE = "READ_ONLY_MODE"
    LIMITED_FUNCTIONALITY = "LIMITED_FUNCTIONALITY"
    DEPENDENCY_ISOLATION = "DEPENDENCY_ISOLATION"
    EMERGENCY_MODE = "EMERGENCY_MODE"
    SHUTDOWN_REQUIRED = "SHUTDOWN_REQUIRED"


@dataclass
class DegradationResult:
    recommended_strategy: DegradationStrategy
    auto_traffic_switch_blocked: bool
    summary: str
    affected_features: List[str]
    details: Dict[str, Any]
    evidence_level: ReliabilityEvidenceLevel


class DegradationManager:
    """Evaluates platform degradation triggers and generates recommendations. Traffic modification is blocked."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_degradation(
        self,
        database_available: bool = True,
        redis_available: bool = True,
        high_latency: bool = False,
        critical_error_rate: bool = False,
        executed: bool = True,
    ) -> DegradationResult:
        if not executed:
            return DegradationResult(
                recommended_strategy=DegradationStrategy.FULL_SERVICE,
                auto_traffic_switch_blocked=True,
                summary="Degradation management not executed.",
                affected_features=[],
                details={"message": "Not executed."},
                evidence_level=self.evidence_level,
            )

        if not database_available and not redis_available:
            strategy = DegradationStrategy.EMERGENCY_MODE
            affected = ["all_write_ops", "caching", "sessions", "analytics"]
        elif not database_available:
            strategy = DegradationStrategy.READ_ONLY_MODE
            affected = ["write_ops", "user_registration", "updates"]
        elif not redis_available or high_latency:
            strategy = DegradationStrategy.GRACEFUL_DEGRADATION
            affected = ["caching", "non_critical_background_jobs"]
        elif critical_error_rate:
            strategy = DegradationStrategy.LIMITED_FUNCTIONALITY
            affected = ["heavy_ai_inference", "batch_processing"]
        else:
            strategy = DegradationStrategy.FULL_SERVICE
            affected = []

        return DegradationResult(
            recommended_strategy=strategy,
            auto_traffic_switch_blocked=True,  # STRICT SAFETY RULE
            summary=f"Degradation evaluation recommends strategy: {strategy.value}. Production traffic unmodified.",
            affected_features=affected,
            details={
                "database_available": database_available,
                "redis_available": redis_available,
                "high_latency": high_latency,
                "critical_error_rate": critical_error_rate,
            },
            evidence_level=self.evidence_level,
        )
