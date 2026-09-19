"""
Phase 5.70 - Recovery State Machine Module.

Enforces valid recovery lifecycle state transitions, maintains immutable transition history, and emits evidence.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceCollector, ReliabilityEvidenceLevel


class RecoveryState(str, Enum):
    NORMAL = "NORMAL"
    INCIDENT_DETECTED = "INCIDENT_DETECTED"
    DEGRADED = "DEGRADED"
    RECOVERY_ANALYSIS = "RECOVERY_ANALYSIS"
    RECOVERY_PLAN_CREATED = "RECOVERY_PLAN_CREATED"
    BACKUP_VALIDATING = "BACKUP_VALIDATING"
    RESTORE_PREPARING = "RESTORE_PREPARING"
    FAILOVER_PREPARING = "FAILOVER_PREPARING"
    RECOVERY_EXECUTING = "RECOVERY_EXECUTING"
    RECOVERY_VALIDATING = "RECOVERY_VALIDATING"
    RECOVERED = "RECOVERED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    NOT_EXECUTED = "NOT_EXECUTED"


class IllegalRecoveryTransitionError(Exception):
    """Raised when an invalid state transition is attempted in the recovery state machine."""


@dataclass
class RecoveryStateTransition:
    from_state: RecoveryState
    to_state: RecoveryState
    timestamp: float
    reason: str
    evidence_fingerprint: str
    details: Dict[str, Any] = field(default_factory=dict)


class RecoveryStateMachine:
    """Manages system recovery lifecycle states and enforces strict transition graph rules."""

    ALLOWED_TRANSITIONS: Dict[RecoveryState, List[RecoveryState]] = {
        RecoveryState.NORMAL: [
            RecoveryState.INCIDENT_DETECTED,
            RecoveryState.DEGRADED,
            RecoveryState.NOT_EXECUTED,
        ],
        RecoveryState.INCIDENT_DETECTED: [
            RecoveryState.DEGRADED,
            RecoveryState.RECOVERY_ANALYSIS,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.FAILED,
        ],
        RecoveryState.DEGRADED: [
            RecoveryState.RECOVERY_ANALYSIS,
            RecoveryState.NORMAL,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.FAILED,
        ],
        RecoveryState.RECOVERY_ANALYSIS: [
            RecoveryState.RECOVERY_PLAN_CREATED,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.BLOCKED,
            RecoveryState.FAILED,
        ],
        RecoveryState.RECOVERY_PLAN_CREATED: [
            RecoveryState.BACKUP_VALIDATING,
            RecoveryState.RESTORE_PREPARING,
            RecoveryState.FAILOVER_PREPARING,
            RecoveryState.RECOVERY_EXECUTING,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.BLOCKED,
        ],
        RecoveryState.BACKUP_VALIDATING: [
            RecoveryState.RESTORE_PREPARING,
            RecoveryState.FAILOVER_PREPARING,
            RecoveryState.RECOVERY_EXECUTING,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.BLOCKED,
            RecoveryState.FAILED,
        ],
        RecoveryState.RESTORE_PREPARING: [
            RecoveryState.RECOVERY_EXECUTING,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.BLOCKED,
            RecoveryState.FAILED,
        ],
        RecoveryState.FAILOVER_PREPARING: [
            RecoveryState.RECOVERY_EXECUTING,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.BLOCKED,
            RecoveryState.FAILED,
        ],
        RecoveryState.RECOVERY_EXECUTING: [
            RecoveryState.RECOVERY_VALIDATING,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.FAILED,
            RecoveryState.BLOCKED,
        ],
        RecoveryState.RECOVERY_VALIDATING: [
            RecoveryState.RECOVERED,
            RecoveryState.DEGRADED,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.FAILED,
        ],
        RecoveryState.RECOVERED: [
            RecoveryState.NORMAL,
            RecoveryState.DEGRADED,
            RecoveryState.INCIDENT_DETECTED,
        ],
        RecoveryState.MANUAL_INTERVENTION_REQUIRED: [
            RecoveryState.RECOVERY_ANALYSIS,
            RecoveryState.RECOVERY_EXECUTING,
            RecoveryState.RECOVERED,
            RecoveryState.FAILED,
            RecoveryState.BLOCKED,
        ],
        RecoveryState.BLOCKED: [
            RecoveryState.RECOVERY_ANALYSIS,
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.NORMAL,
        ],
        RecoveryState.FAILED: [
            RecoveryState.MANUAL_INTERVENTION_REQUIRED,
            RecoveryState.RECOVERY_ANALYSIS,
        ],
        RecoveryState.NOT_EXECUTED: [
            RecoveryState.NORMAL,
        ],
    }

    def __init__(
        self,
        initial_state: RecoveryState = RecoveryState.NORMAL,
        evidence_collector: Optional[ReliabilityEvidenceCollector] = None,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self._current_state = initial_state
        self._history: List[RecoveryStateTransition] = []
        self.evidence_collector = evidence_collector or ReliabilityEvidenceCollector()
        self.evidence_level = evidence_level

    @property
    def current_state(self) -> RecoveryState:
        return self._current_state

    @property
    def history(self) -> List[RecoveryStateTransition]:
        return list(self._history)

    def transition_to(
        self,
        to_state: RecoveryState,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> RecoveryStateTransition:
        if details is None:
            details = {}

        allowed = self.ALLOWED_TRANSITIONS.get(self._current_state, [])
        if to_state not in allowed:
            raise IllegalRecoveryTransitionError(
                f"Illegal recovery transition from {self._current_state.value} to {to_state.value}. Reason: {reason}"
            )

        now = time.time()
        ev = self.evidence_collector.collect_evidence(
            component="RecoveryStateMachine",
            event=f"transition:{self._current_state.value}->{to_state.value}",
            status="SUCCESS",
            evidence_level=self.evidence_level,
            raw_payload={
                "from_state": self._current_state.value,
                "to_state": to_state.value,
                "reason": reason,
                "details": details,
            },
            timestamp=now,
        )

        transition = RecoveryStateTransition(
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
