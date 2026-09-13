"""
Phase 5.70 - Dependency Resilience Module.

Evaluates resilience for critical platform dependencies (PostgreSQL, Redis, Prometheus, EventBus, Authentication, Secret Provider, External APIs).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class DependencyState(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    RECOVERING = "RECOVERING"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class DependencyFailureScenario:
    name: str
    target_dependency: str
    simulated_state: DependencyState
    fallback_available: bool
    recovery_time_seconds: float


@dataclass
class DependencyResilienceResult:
    overall_resilience_score: float
    dependencies: Dict[str, DependencyState]
    scenarios_evaluated: List[DependencyFailureScenario]
    unhandled_dependencies: List[str]
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class DependencyResilienceEvaluator:
    """Evaluates platform resilience against single and multi-dependency failures."""

    STANDARD_DEPENDENCIES = [
        "postgresql",
        "redis",
        "prometheus",
        "event_bus",
        "authentication",
        "secret_provider",
        "external_apis",
    ]

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_dependencies(
        self,
        dependency_states: Optional[Dict[str, DependencyState]] = None,
        scenarios: Optional[List[DependencyFailureScenario]] = None,
        executed: bool = True,
    ) -> DependencyResilienceResult:
        if not executed:
            return DependencyResilienceResult(
                overall_resilience_score=0.0,
                dependencies={},
                scenarios_evaluated=[],
                unhandled_dependencies=self.STANDARD_DEPENDENCIES,
                evidence_level=self.evidence_level,
                details={"message": "Dependency resilience evaluation not executed."},
            )

        if dependency_states is None:
            dependency_states = {dep: DependencyState.AVAILABLE for dep in self.STANDARD_DEPENDENCIES}

        if scenarios is None:
            scenarios = []

        unhandled: List[str] = []
        scores: List[float] = []

        for dep in self.STANDARD_DEPENDENCIES:
            state = dependency_states.get(dep, DependencyState.NOT_EXECUTED)
            if state == DependencyState.AVAILABLE:
                scores.append(100.0)
            elif state == DependencyState.DEGRADED:
                scores.append(75.0)
            elif state == DependencyState.RECOVERING:
                scores.append(50.0)
            elif state == DependencyState.UNAVAILABLE:
                # Check if there is a scenario with a working fallback
                dep_scenarios = [s for s in scenarios if s.target_dependency == dep and s.fallback_available]
                if dep_scenarios:
                    scores.append(60.0)
                else:
                    scores.append(0.0)
                    unhandled.append(dep)
            else:
                scores.append(0.0)

        # Division by zero protection
        count = len(scores)
        overall_score = round(sum(scores) / count, 2) if count > 0 else 0.0

        return DependencyResilienceResult(
            overall_resilience_score=overall_score,
            dependencies=dependency_states,
            scenarios_evaluated=scenarios,
            unhandled_dependencies=unhandled,
            evidence_level=self.evidence_level,
            details={"scenarios_count": len(scenarios)},
        )
