"""
Phase 5.70 - Failover Engine Module.

Evaluates primary, database, region, service, and dependency failover plans.
Strict Safety Rule: Failover execution defaults to auto_execution_blocked = True.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class FailoverTrigger(str, Enum):
    PRIMARY_FAILURE = "PRIMARY_FAILURE"
    DATABASE_FAILURE = "DATABASE_FAILURE"
    REGION_FAILURE = "REGION_FAILURE"
    SERVICE_FAILURE = "SERVICE_FAILURE"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"


class FailoverState(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    READY = "READY"
    RECOMMENDED = "RECOMMENDED"
    MANUAL_EXECUTION_REQUIRED = "MANUAL_EXECUTION_REQUIRED"
    EXECUTED = "EXECUTED"
    VALIDATED = "VALIDATED"
    BLOCKED = "BLOCKED"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class FailoverPlan:
    plan_id: str
    trigger: FailoverTrigger
    source_target: str
    destination_target: str
    rto_seconds: float = 300.0  # 5 minutes
    steps: List[str] = field(default_factory=list)


@dataclass
class FailoverResult:
    plan_id: str
    trigger: FailoverTrigger
    state: FailoverState
    auto_execution_blocked: bool
    production_failover_executed: bool
    summary: str
    details: Dict[str, Any]
    evidence_level: ReliabilityEvidenceLevel


class FailoverEngine:
    """Evaluates failover readiness and generates recommendations. Auto execution is strictly blocked."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_failover(
        self,
        plan: FailoverPlan,
        trigger_active: bool = False,
        real_production_executed: bool = False,
        executed: bool = True,
    ) -> FailoverResult:
        if not executed:
            return FailoverResult(
                plan_id=plan.plan_id,
                trigger=plan.trigger,
                state=FailoverState.NOT_EXECUTED,
                auto_execution_blocked=True,
                production_failover_executed=False,
                summary="Failover evaluation not executed.",
                details={"message": "Not executed."},
                evidence_level=self.evidence_level,
            )

        if not trigger_active:
            state = FailoverState.READY
            summary = f"Failover plan {plan.plan_id} is READY for trigger {plan.trigger.value}."
        else:
            state = FailoverState.RECOMMENDED
            summary = f"Failover RECOMMENDED for trigger {plan.trigger.value}. Auto-execution blocked; manual review required."

        if real_production_executed:
            state = FailoverState.EXECUTED
            summary = f"Failover EXECUTED for plan {plan.plan_id} on real production target."

        return FailoverResult(
            plan_id=plan.plan_id,
            trigger=plan.trigger,
            state=state,
            auto_execution_blocked=True,  # STRICT SAFETY RULE
            production_failover_executed=real_production_executed,
            summary=summary,
            details={
                "trigger_active": trigger_active,
                "source": plan.source_target,
                "destination": plan.destination_target,
            },
            evidence_level=self.evidence_level,
        )
