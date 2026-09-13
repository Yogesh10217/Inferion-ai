"""
Phase 5.70 - Chaos State Machine Module.

Enforces deterministic lifecycle transitions for chaos experiments.
Illegal transitions raise IllegalStateTransitionError.
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceCollector, ReliabilityEvidenceLevel


class ChaosState(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    AUTHORIZED = "AUTHORIZED"
    RUNNING = "RUNNING"
    FAILURE_INJECTED = "FAILURE_INJECTED"
    OBSERVING = "OBSERVING"
    RECOVERING = "RECOVERING"
    VALIDATING_RECOVERY = "VALIDATING_RECOVERY"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"
    RECOVERY_FAILED = "RECOVERY_FAILED"


class IllegalStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted in the Chaos State Machine."""

    pass


@dataclass
class ChaosStateTransition:
    from_state: ChaosState
    to_state: ChaosState
    timestamp: float
    reason: str
    evidence_fingerprint: str
    details: Dict[str, Any] = field(default_factory=dict)


class ChaosStateMachine:
    """Manages the state transitions of a chaos experiment."""

    ALLOWED_TRANSITIONS: Dict[ChaosState, List[ChaosState]] = {
        ChaosState.CREATED: [ChaosState.VALIDATING, ChaosState.ABORTED, ChaosState.BLOCKED],
        ChaosState.VALIDATING: [ChaosState.AUTHORIZED, ChaosState.BLOCKED, ChaosState.FAILED, ChaosState.ABORTED],
        ChaosState.AUTHORIZED: [ChaosState.RUNNING, ChaosState.ABORTED, ChaosState.BLOCKED],
        ChaosState.RUNNING: [ChaosState.FAILURE_INJECTED, ChaosState.FAILED, ChaosState.ABORTED, ChaosState.BLOCKED],
        ChaosState.FAILURE_INJECTED: [ChaosState.OBSERVING, ChaosState.FAILED, ChaosState.RECOVERY_FAILED, ChaosState.ABORTED],
        ChaosState.OBSERVING: [ChaosState.RECOVERING, ChaosState.FAILED, ChaosState.RECOVERY_FAILED, ChaosState.ABORTED],
        ChaosState.RECOVERING: [ChaosState.VALIDATING_RECOVERY, ChaosState.RECOVERY_FAILED, ChaosState.FAILED, ChaosState.ABORTED],
        ChaosState.VALIDATING_RECOVERY: [ChaosState.COMPLETED, ChaosState.RECOVERY_FAILED, ChaosState.FAILED, ChaosState.ABORTED],
        ChaosState.COMPLETED: [],
        ChaosState.BLOCKED: [],
        ChaosState.FAILED: [],
        ChaosState.ABORTED: [],
        ChaosState.RECOVERY_FAILED: [],
    }

    def __init__(
        self,
        experiment_id: str,
        initial_state: ChaosState = ChaosState.CREATED,
        evidence_collector: Optional[ReliabilityEvidenceCollector] = None,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self.experiment_id = experiment_id
        self._current_state = initial_state
        self._history: List[ChaosStateTransition] = []
        self.evidence_collector = evidence_collector or ReliabilityEvidenceCollector()
        self.evidence_level = evidence_level

    @property
    def current_state(self) -> ChaosState:
        return self._current_state

    @property
    def history(self) -> List[ChaosStateTransition]:
        return list(self._history)

    def transition_to(
        self,
        to_state: ChaosState,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> ChaosStateTransition:
        if details is None:
            details = {}

        allowed = self.ALLOWED_TRANSITIONS.get(self._current_state, [])
        if to_state not in allowed:
            raise IllegalStateTransitionError(
                f"Illegal chaos state transition for experiment {self.experiment_id}: {self._current_state.value} -> {to_state.value}. Reason: {reason}"
            )

        now = time.time()
        ev = self.evidence_collector.collect_evidence(
            component="ChaosStateMachine",
            event=f"chaos_transition:{self._current_state.value}->{to_state.value}",
            status="SUCCESS" if to_state not in (ChaosState.BLOCKED, ChaosState.FAILED, ChaosState.RECOVERY_FAILED) else "FAILED",
            evidence_level=self.evidence_level,
            raw_payload={
                "experiment_id": self.experiment_id,
                "from_state": self._current_state.value,
                "to_state": to_state.value,
                "reason": reason,
                "details": details,
            },
            timestamp=now,
        )

        transition = ChaosStateTransition(
            from_state=self._current_state,
            to_state=to_state,
            timestamp=now,
            reason=reason,
            evidence_fingerprint=ev.fingerprint,
            details=details,
        )

        self._history.append(transition)
        self._current_state = to_state
        return transition
