"""
Incident State Machine Module for Phase 5.68.
Defines 11 deterministic incident lifecycle states and strictly enforces valid state transitions.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Set


class IncidentState(str, Enum):
    NOT_DETECTED = "NOT_DETECTED"
    DETECTED = "DETECTED"
    TRIAGING = "TRIAGING"
    CONFIRMED = "CONFIRMED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RECOVERING = "RECOVERING"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"
    POST_INCIDENT_REVIEW_REQUIRED = "POST_INCIDENT_REVIEW_REQUIRED"
    CLOSED = "CLOSED"


class IllegalStateTransitionError(ValueError):
    """Raised when an illegal incident state transition is requested."""
    pass


class IncidentStateMachine:
    """Enforces strict, deterministic state transitions for incident lifecycle management."""

    # Explicit allowed transitions table
    VALID_TRANSITIONS: Dict[IncidentState, Set[IncidentState]] = {
        IncidentState.NOT_DETECTED: {IncidentState.DETECTED},
        IncidentState.DETECTED: {IncidentState.TRIAGING, IncidentState.CLOSED},
        IncidentState.TRIAGING: {IncidentState.CONFIRMED, IncidentState.CLOSED},
        IncidentState.CONFIRMED: {IncidentState.INVESTIGATING, IncidentState.MITIGATING},
        IncidentState.INVESTIGATING: {IncidentState.MITIGATING, IncidentState.RECOVERING},
        IncidentState.MITIGATING: {IncidentState.RECOVERING, IncidentState.MONITORING},
        IncidentState.RECOVERING: {IncidentState.MONITORING, IncidentState.RESOLVED},
        IncidentState.MONITORING: {IncidentState.RESOLVED, IncidentState.MITIGATING},
        IncidentState.RESOLVED: {IncidentState.POST_INCIDENT_REVIEW_REQUIRED, IncidentState.CLOSED},
        IncidentState.POST_INCIDENT_REVIEW_REQUIRED: {IncidentState.CLOSED},
        IncidentState.CLOSED: set(),
    }

    @classmethod
    def transition(cls, current_state: IncidentState, target_state: IncidentState) -> IncidentState:
        if current_state == target_state:
            return target_state

        allowed = cls.VALID_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise IllegalStateTransitionError(
                f"Illegal state transition requested: {current_state.value} -> {target_state.value}. "
                f"Allowed transitions from {current_state.value} are: {[s.value for s in allowed]}"
            )
        return target_state
