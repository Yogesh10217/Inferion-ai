"""Resource Lifecycle State Machine with Transition Hooks & Validation."""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from app.control_plane.exceptions import LifecycleException

logger = logging.getLogger(__name__)


class LifecycleState(str, Enum):
    CREATED = "CREATED"
    PROVISIONING = "PROVISIONING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
    UPDATING = "UPDATING"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"
    FAILED = "FAILED"


VALID_TRANSITIONS = {
    LifecycleState.CREATED: {LifecycleState.PROVISIONING, LifecycleState.ACTIVE, LifecycleState.FAILED},
    LifecycleState.PROVISIONING: {LifecycleState.ACTIVE, LifecycleState.FAILED},
    LifecycleState.ACTIVE: {LifecycleState.PAUSED, LifecycleState.SUSPENDED, LifecycleState.UPDATING, LifecycleState.DEPRECATED, LifecycleState.ARCHIVED, LifecycleState.DELETED},
    LifecycleState.PAUSED: {LifecycleState.ACTIVE, LifecycleState.DELETED},
    LifecycleState.SUSPENDED: {LifecycleState.ACTIVE, LifecycleState.DELETED},
    LifecycleState.UPDATING: {LifecycleState.ACTIVE, LifecycleState.FAILED},
    LifecycleState.DEPRECATED: {LifecycleState.ARCHIVED, LifecycleState.DELETED},
    LifecycleState.ARCHIVED: {LifecycleState.ACTIVE, LifecycleState.DELETED},
    LifecycleState.FAILED: {LifecycleState.PROVISIONING, LifecycleState.DELETED},
    LifecycleState.DELETED: set(),
}


class LifecycleRecord(BaseModel):
    """Event entry tracking a state transition."""

    resource_id: str
    previous_state: Optional[LifecycleState]
    current_state: LifecycleState
    reason: str
    actor_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LifecycleManager:
    """Enforces valid lifecycle state transitions, transition hooks, and state history."""

    def __init__(self) -> None:
        self._states: Dict[str, LifecycleState] = {}
        self._history: Dict[str, List[LifecycleRecord]] = {}
        self._hooks: List[Callable] = []

    def register_transition_hook(self, hook: Callable) -> None:
        self._hooks.append(hook)

    def get_state(self, resource_id: str) -> LifecycleState:
        return self._states.get(resource_id, LifecycleState.CREATED)

    def transition(
        self,
        resource_id: str,
        target_state: LifecycleState,
        reason: str = "State transition",
        actor_id: str = "system",
    ) -> LifecycleRecord:
        """Validate and execute a lifecycle state transition."""
        current = self.get_state(resource_id)

        if current != target_state and target_state not in VALID_TRANSITIONS.get(current, set()):
            raise LifecycleException(
                f"Invalid lifecycle transition for resource '{resource_id}': {current.value} -> {target_state.value}"
            )

        self._states[resource_id] = target_state
        rec = LifecycleRecord(
            resource_id=resource_id,
            previous_state=current,
            current_state=target_state,
            reason=reason,
            actor_id=actor_id,
        )

        if resource_id not in self._history:
            self._history[resource_id] = []
        self._history[resource_id].append(rec)

        # Trigger hooks
        for hook in self._hooks:
            try:
                hook(rec)
            except Exception as e:
                logger.error(f"[LIFECYCLE HOOK ERROR] Hook failed for '{resource_id}': {e}")

        logger.info(f"[LIFECYCLE MANAGER] '{resource_id}' transitioned {current.value} -> {target_state.value}")
        return rec

    def get_history(self, resource_id: str) -> List[LifecycleRecord]:
        return list(self._history.get(resource_id, []))
