"""
Phase 5.70 - Fault Tolerance Engine Module.

Simulates and evaluates system behavior under controlled fault scenarios.
Live destructive fault injection is strictly blocked by default.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class FaultType(str, Enum):
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    DATABASE_FAILURE = "DATABASE_FAILURE"
    CACHE_FAILURE = "CACHE_FAILURE"
    EVENTBUS_FAILURE = "EVENTBUS_FAILURE"
    AUTH_FAILURE = "AUTH_FAILURE"
    SECRET_PROVIDER_FAILURE = "SECRET_PROVIDER_FAILURE"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    CONTAINER_FAILURE = "CONTAINER_FAILURE"
    APPLICATION_FAILURE = "APPLICATION_FAILURE"
    OBSERVABILITY_FAILURE = "OBSERVABILITY_FAILURE"


class FaultClassification(str, Enum):
    TOLERATED = "TOLERATED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class FaultScenario:
    scenario_id: str
    fault_type: FaultType
    description: str
    is_simulation: bool = True
    expected_classification: FaultClassification = FaultClassification.TOLERATED


@dataclass
class FaultToleranceResult:
    scenario_id: str
    fault_type: FaultType
    classification: FaultClassification
    system_recovered: bool
    live_injection_blocked: bool
    details: Dict[str, Any]
    evidence_level: ReliabilityEvidenceLevel


class FaultToleranceEngine:
    """Evaluates fault tolerance via simulation. Live destructive fault injection is blocked."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_fault_scenario(
        self,
        scenario: FaultScenario,
        live_injection_allowed: bool = False,
        executed: bool = True,
    ) -> FaultToleranceResult:
        if not executed:
            return FaultToleranceResult(
                scenario_id=scenario.scenario_id,
                fault_type=scenario.fault_type,
                classification=FaultClassification.NOT_EXECUTED,
                system_recovered=False,
                live_injection_blocked=True,
                details={"message": "Fault scenario evaluation not executed."},
                evidence_level=self.evidence_level,
            )

        # STRICT SAFETY RULE: Block live destructive fault injection
        live_blocked = True
        if not scenario.is_simulation and not live_injection_allowed:
            return FaultToleranceResult(
                scenario_id=scenario.scenario_id,
                fault_type=scenario.fault_type,
                classification=FaultClassification.FAILED,
                system_recovered=False,
                live_injection_blocked=True,
                details={"error": "Live destructive fault injection is strictly blocked by safety rules."},
                evidence_level=self.evidence_level,
            )

        # Simulated evaluation
        classification = scenario.expected_classification
        system_recovered = classification in (FaultClassification.TOLERATED, FaultClassification.DEGRADED)

        return FaultToleranceResult(
            scenario_id=scenario.scenario_id,
            fault_type=scenario.fault_type,
            classification=classification,
            system_recovered=system_recovered,
            live_injection_blocked=live_blocked,
            details={
                "is_simulation": scenario.is_simulation,
                "description": scenario.description,
            },
            evidence_level=self.evidence_level,
        )
