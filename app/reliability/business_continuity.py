"""
Phase 5.70 - Business Continuity Engine Module.

Evaluates critical service continuity, recovery sequences, operational fallback readiness, and minimum service capability.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class ContinuityClassification(str, Enum):
    CONTINUITY_READY = "CONTINUITY_READY"
    CONTINUITY_WARNING = "CONTINUITY_WARNING"
    CONTINUITY_AT_RISK = "CONTINUITY_AT_RISK"
    CONTINUITY_BLOCKED = "CONTINUITY_BLOCKED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class BusinessContinuityPlan:
    plan_id: str
    name: str
    critical_services_defined: bool = True
    recovery_sequence_defined: bool = True
    communication_plan_ready: bool = True
    minimum_capability_percentage: float = 80.0


@dataclass
class BusinessContinuityResult:
    plan_id: str
    classification: ContinuityClassification
    minimum_capability_met: bool
    production_bc_executed: bool  # Strict truthfulness flag
    summary: str
    details: Dict[str, Any]
    evidence_level: ReliabilityEvidenceLevel


class BusinessContinuityEngine:
    """Evaluates Business Continuity readiness across critical business capabilities."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_continuity(
        self,
        plan: BusinessContinuityPlan,
        simulated_capability_percentage: float = 90.0,
        real_production_executed: bool = False,
        executed: bool = True,
    ) -> BusinessContinuityResult:
        if not executed:
            return BusinessContinuityResult(
                plan_id=plan.plan_id,
                classification=ContinuityClassification.NOT_EXECUTED,
                minimum_capability_met=False,
                production_bc_executed=False,
                summary="Business continuity evaluation not executed.",
                details={"message": "Not executed."},
                evidence_level=self.evidence_level,
            )

        min_met = simulated_capability_percentage >= plan.minimum_capability_percentage

        if not plan.critical_services_defined or not plan.recovery_sequence_defined:
            classification = ContinuityClassification.CONTINUITY_BLOCKED
        elif not min_met:
            classification = ContinuityClassification.CONTINUITY_AT_RISK
        elif not plan.communication_plan_ready:
            classification = ContinuityClassification.CONTINUITY_WARNING
        else:
            classification = ContinuityClassification.CONTINUITY_READY

        return BusinessContinuityResult(
            plan_id=plan.plan_id,
            classification=classification,
            minimum_capability_met=min_met,
            production_bc_executed=real_production_executed,  # Strictly False unless real execution occurred
            summary=f"Business Continuity Plan {plan.plan_id} evaluated as {classification.value}.",
            details={
                "simulated_capability_percentage": simulated_capability_percentage,
                "minimum_target_percentage": plan.minimum_capability_percentage,
            },
            evidence_level=self.evidence_level,
        )
