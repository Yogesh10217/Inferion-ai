"""Reusable Lifecycle State Machine Framework (Phase 5.30)."""

from typing import List, Set

from pydantic import BaseModel, Field

from app.platform_contracts.exceptions import InvalidLifecycleTransitionException


class LifecycleState(BaseModel):
    name: str
    is_terminal: bool = False


class LifecycleTransition(BaseModel):
    from_state: str
    to_state: str


class LifecycleMachine(BaseModel):
    name: str
    initial_state: str
    valid_transitions: List[LifecycleTransition] = Field(default_factory=list)
    terminal_states: Set[str] = Field(default_factory=set)

    def validate_transition(self, current_state: str, target_state: str) -> bool:
        if current_state == target_state:
            return True
        for tr in self.valid_transitions:
            if tr.from_state == current_state and tr.to_state == target_state:
                return True
        raise InvalidLifecycleTransitionException(current_state, target_state)
