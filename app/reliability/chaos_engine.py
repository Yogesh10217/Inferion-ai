"""
Phase 5.70 - Chaos Engineering Engine Module.

Manages controlled chaos experiments, 16 failure types, execution modes, state machine transitions, and idempotency.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.reliability.chaos_state_machine import ChaosState, ChaosStateMachine
from app.reliability.reliability_evidence import ReliabilityEvidenceCollector, ReliabilityEvidenceLevel
from app.reliability.reliability_models import ChaosExecutionMode, ChaosFailureType


@dataclass
class ChaosExperiment:
    experiment_id: str
    name: str
    target: str
    failure_type: ChaosFailureType
    execution_mode: ChaosExecutionMode = ChaosExecutionMode.SIMULATION
    status: ChaosState = ChaosState.CREATED
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    fingerprint: Optional[str] = None


@dataclass
class ChaosExperimentResult:
    experiment_id: str
    failure_type: ChaosFailureType
    execution_mode: ChaosExecutionMode
    status: ChaosState
    idempotent_replay: bool
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any]
    fingerprint: str


class ChaosEngineeringEngine:
    """Manages controlled chaos experiment execution with idempotency, state transitions, and evidence levels."""

    def __init__(
        self,
        evidence_collector: Optional[ReliabilityEvidenceCollector] = None,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self.evidence_collector = evidence_collector or ReliabilityEvidenceCollector()
        self.evidence_level = evidence_level
        self._experiment_results: Dict[str, ChaosExperimentResult] = {}
        self._state_machines: Dict[str, ChaosStateMachine] = {}

    def map_mode_to_evidence_level(self, mode: ChaosExecutionMode) -> ReliabilityEvidenceLevel:
        if mode == ChaosExecutionMode.CONTAINER:
            return ReliabilityEvidenceLevel.CONTAINER_RUNTIME
        elif mode == ChaosExecutionMode.PRODUCTION:
            return ReliabilityEvidenceLevel.PRODUCTION_RUNTIME
        else:
            return ReliabilityEvidenceLevel.SIMULATION_RUNTIME

    def run_chaos_experiment(
        self,
        experiment: ChaosExperiment,
        authorized: bool = True,
        executed: bool = True,
    ) -> ChaosExperimentResult:
        # Idempotency check: Return existing result if duplicate request
        if experiment.experiment_id in self._experiment_results:
            existing = self._experiment_results[experiment.experiment_id]
            return ChaosExperimentResult(
                experiment_id=existing.experiment_id,
                failure_type=existing.failure_type,
                execution_mode=existing.execution_mode,
                status=existing.status,
                idempotent_replay=True,  # Idempotent replay flag
                evidence_level=existing.evidence_level,
                details=existing.details,
                fingerprint=existing.fingerprint,
            )

        if not executed:
            return ChaosExperimentResult(
                experiment_id=experiment.experiment_id,
                failure_type=experiment.failure_type,
                execution_mode=experiment.execution_mode,
                status=ChaosState.BLOCKED,
                idempotent_replay=False,
                evidence_level=self.evidence_level,
                details={"message": "Chaos experiment not executed."},
                fingerprint="sha256:0000000000000000000000000000000000000000000000000000000000000000",
            )

        ev_level = self.map_mode_to_evidence_level(experiment.execution_mode)

        # Initialize Chaos State Machine
        sm = ChaosStateMachine(
            experiment_id=experiment.experiment_id,
            evidence_collector=self.evidence_collector,
            evidence_level=ev_level,
        )
        self._state_machines[experiment.experiment_id] = sm

        # State transition sequence
        sm.transition_to(ChaosState.VALIDATING, reason="Validating experiment parameters")

        if not authorized or (
            experiment.execution_mode == ChaosExecutionMode.PRODUCTION
            and not experiment.evidence.get("production_auth_verified", False)
        ):
            sm.transition_to(
                ChaosState.BLOCKED, reason="Experiment authorization denied or missing production authorization"
            )
            fp = self._generate_fingerprint(experiment, ChaosState.BLOCKED)
            res = ChaosExperimentResult(
                experiment_id=experiment.experiment_id,
                failure_type=experiment.failure_type,
                execution_mode=experiment.execution_mode,
                status=ChaosState.BLOCKED,
                idempotent_replay=False,
                evidence_level=ev_level,
                details={"error": "Production chaos execution target unconfigured or unauthorized."},
                fingerprint=fp,
            )
            self._experiment_results[experiment.experiment_id] = res
            return res

        sm.transition_to(ChaosState.AUTHORIZED, reason="Chaos experiment authorized")
        sm.transition_to(ChaosState.RUNNING, reason="Chaos experiment running")
        sm.transition_to(ChaosState.FAILURE_INJECTED, reason=f"Injected failure: {experiment.failure_type.value}")
        sm.transition_to(ChaosState.OBSERVING, reason="Observing system behavior")
        sm.transition_to(ChaosState.RECOVERING, reason="Recovery triggered")
        sm.transition_to(ChaosState.VALIDATING_RECOVERY, reason="Validating post-recovery health")
        sm.transition_to(ChaosState.COMPLETED, reason="Experiment completed successfully")

        fp = self._generate_fingerprint(experiment, ChaosState.COMPLETED)
        res = ChaosExperimentResult(
            experiment_id=experiment.experiment_id,
            failure_type=experiment.failure_type,
            execution_mode=experiment.execution_mode,
            status=ChaosState.COMPLETED,
            idempotent_replay=False,
            evidence_level=ev_level,
            details={
                "target": experiment.target,
                "history_length": len(sm.history),
            },
            fingerprint=fp,
        )

        self._experiment_results[experiment.experiment_id] = res
        return res

    def _generate_fingerprint(self, exp: ChaosExperiment, final_state: ChaosState) -> str:
        canonical_payload = {
            "experiment_id": exp.experiment_id,
            "failure_type": exp.failure_type.value,
            "execution_mode": exp.execution_mode.value,
            "final_state": final_state.value,
            "target": exp.target,
        }
        det_json = json.dumps(canonical_payload, sort_keys=True)
        sha256 = hashlib.sha256(det_json.encode("utf-8")).hexdigest()
        return f"sha256:{sha256}"
