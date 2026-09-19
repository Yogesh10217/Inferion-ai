"""Runtime Lifecycle State Machine for Phase 5.57 Runtime Intelligence."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Set

from app.runtime_intelligence.exceptions import InvalidRuntimeStateTransitionException

logger = logging.getLogger(__name__)


class RuntimeLifecycleState(str, Enum):
    OBSERVED = "OBSERVED"
    ANALYZING = "ANALYZING"
    HEALTH_ASSESSED = "HEALTH_ASSESSED"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    RISK_ASSESSED = "RISK_ASSESSED"
    ADAPTATION_RECOMMENDED = "ADAPTATION_RECOMMENDED"
    GOVERNANCE_EVALUATED = "GOVERNANCE_EVALUATED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    VERIFYING = "VERIFYING"
    STABILIZED = "STABILIZED"
    CLOSED = "CLOSED"

    # Terminal / Outcome States
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    DEGRADED = "DEGRADED"


# Valid state transitions graph
VALID_TRANSITIONS: Dict[RuntimeLifecycleState, Set[RuntimeLifecycleState]] = {
    RuntimeLifecycleState.OBSERVED: {
        RuntimeLifecycleState.ANALYZING,
        RuntimeLifecycleState.FAILED,
        RuntimeLifecycleState.CANCELLED,
    },
    RuntimeLifecycleState.ANALYZING: {
        RuntimeLifecycleState.HEALTH_ASSESSED,
        RuntimeLifecycleState.FAILED,
        RuntimeLifecycleState.CANCELLED,
    },
    RuntimeLifecycleState.HEALTH_ASSESSED: {
        RuntimeLifecycleState.ANOMALY_DETECTED,
        RuntimeLifecycleState.RISK_ASSESSED,
        RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.ANOMALY_DETECTED: {
        RuntimeLifecycleState.RISK_ASSESSED,
        RuntimeLifecycleState.DEGRADED,
        RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.RISK_ASSESSED: {
        RuntimeLifecycleState.ADAPTATION_RECOMMENDED,
        RuntimeLifecycleState.CLOSED,
        RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.ADAPTATION_RECOMMENDED: {
        RuntimeLifecycleState.GOVERNANCE_EVALUATED,
        RuntimeLifecycleState.CLOSED,
        RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.GOVERNANCE_EVALUATED: {
        RuntimeLifecycleState.REQUIRES_APPROVAL,
        RuntimeLifecycleState.APPROVED,
        RuntimeLifecycleState.REJECTED,
        RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.REQUIRES_APPROVAL: {
        RuntimeLifecycleState.APPROVED,
        RuntimeLifecycleState.REJECTED,
        RuntimeLifecycleState.CANCELLED,
    },
    RuntimeLifecycleState.APPROVED: {
        RuntimeLifecycleState.DELEGATED,
        RuntimeLifecycleState.CANCELLED,
        RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.DELEGATED: {RuntimeLifecycleState.VERIFYING, RuntimeLifecycleState.FAILED},
    RuntimeLifecycleState.VERIFYING: {
        RuntimeLifecycleState.STABILIZED,
        RuntimeLifecycleState.DEGRADED,
        RuntimeLifecycleState.FAILED,
    },
    RuntimeLifecycleState.STABILIZED: {RuntimeLifecycleState.CLOSED},
    RuntimeLifecycleState.CLOSED: set(),
    RuntimeLifecycleState.REJECTED: set(),
    RuntimeLifecycleState.CANCELLED: set(),
    RuntimeLifecycleState.FAILED: set(),
    RuntimeLifecycleState.DEGRADED: {
        RuntimeLifecycleState.ANALYZING,
        RuntimeLifecycleState.FAILED,
        RuntimeLifecycleState.CLOSED,
    },
}


@dataclass
class RuntimeStateTransitionRecord:
    from_state: RuntimeLifecycleState
    to_state: RuntimeLifecycleState
    reason: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeLifecycleManager:
    """Enforces strict state machine transitions for runtime intelligence operations."""

    def __init__(self, initial_state: RuntimeLifecycleState = RuntimeLifecycleState.OBSERVED) -> None:
        self.current_state = initial_state
        self.history: List[RuntimeStateTransitionRecord] = []

    def transition_to(self, target_state: RuntimeLifecycleState, reason: str = "") -> RuntimeLifecycleState:
        allowed = VALID_TRANSITIONS.get(self.current_state, set())
        if target_state not in allowed:
            logger.error(f"Illegal transition attempted: {self.current_state} -> {target_state}")
            raise InvalidRuntimeStateTransitionException(
                from_state=self.current_state.value, to_state=target_state.value
            )
        rec = RuntimeStateTransitionRecord(from_state=self.current_state, to_state=target_state, reason=reason)
        self.history.append(rec)
        self.current_state = target_state
        logger.info(f"Runtime lifecycle transitioned to {target_state.value}: {reason}")
        return self.current_state
