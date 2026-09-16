"""Lifecycle state transition machine for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Set

from app.continuous_assurance.exceptions import InvalidContinuousAssuranceStateTransitionException
from app.continuous_assurance.models import AssuranceLifecycleState

logger = logging.getLogger(__name__)


class AssuranceLifecycleMachine:
    """Enforces valid state transitions in continuous assurance assessments."""

    ALLOWED_TRANSITIONS: Dict[AssuranceLifecycleState, Set[AssuranceLifecycleState]] = {
        AssuranceLifecycleState.INITIALIZING: {AssuranceLifecycleState.MONITORING, AssuranceLifecycleState.CLOSED},
        AssuranceLifecycleState.MONITORING: {
            AssuranceLifecycleState.STABLE,
            AssuranceLifecycleState.DEGRADED,
            AssuranceLifecycleState.AT_RISK,
            AssuranceLifecycleState.CRITICAL,
        },
        AssuranceLifecycleState.STABLE: {
            AssuranceLifecycleState.MONITORING,
            AssuranceLifecycleState.DEGRADED,
            AssuranceLifecycleState.AT_RISK,
        },
        AssuranceLifecycleState.DEGRADED: {
            AssuranceLifecycleState.AT_RISK,
            AssuranceLifecycleState.CRITICAL,
            AssuranceLifecycleState.RECOVERING,
            AssuranceLifecycleState.STABLE,
        },
        AssuranceLifecycleState.AT_RISK: {
            AssuranceLifecycleState.CRITICAL,
            AssuranceLifecycleState.RECOVERING,
            AssuranceLifecycleState.STABLE,
        },
        AssuranceLifecycleState.CRITICAL: {
            AssuranceLifecycleState.RECOVERING,
            AssuranceLifecycleState.VERIFYING,
            AssuranceLifecycleState.CLOSED,
        },
        AssuranceLifecycleState.RECOVERING: {
            AssuranceLifecycleState.VERIFYING,
            AssuranceLifecycleState.RESTORED,
            AssuranceLifecycleState.CRITICAL,
        },
        AssuranceLifecycleState.VERIFYING: {
            AssuranceLifecycleState.RESTORED,
            AssuranceLifecycleState.STABLE,
            AssuranceLifecycleState.DEGRADED,
            AssuranceLifecycleState.CRITICAL,
        },
        AssuranceLifecycleState.RESTORED: {
            AssuranceLifecycleState.STABLE,
            AssuranceLifecycleState.MONITORING,
            AssuranceLifecycleState.CLOSED,
        },
        AssuranceLifecycleState.CLOSED: set(),
    }

    @classmethod
    def validate_transition(
        cls, current_state: AssuranceLifecycleState, target_state: AssuranceLifecycleState
    ) -> None:
        if current_state == target_state:
            return

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            logger.warning(
                f"Invalid assurance state transition attempted: {current_state.value} -> {target_state.value}"
            )
            raise InvalidContinuousAssuranceStateTransitionException(
                current=current_state.value, target=target_state.value
            )
