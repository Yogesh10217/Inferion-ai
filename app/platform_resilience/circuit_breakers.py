"""Circuit Breaker Intelligence Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import (
    InvalidFailoverTransitionException,
)


class CircuitBreakerState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerPolicy(BaseModel):
    breaker_id: str = Field(default_factory=lambda: f"cbpoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_service_id: str
    failure_threshold: int = 5
    recovery_time_seconds: int = 60
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    consecutive_failures: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CircuitBreakerTransition(BaseModel):
    transition_id: str = Field(default_factory=lambda: f"cbtrans_{uuid.uuid4().hex[:12]}")
    breaker_id: str
    from_state: CircuitBreakerState
    to_state: CircuitBreakerState
    reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CircuitBreakerAssessment(BaseModel):
    breaker_id: str
    tenant_id: str
    target_service_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    is_call_allowed: bool = True


class CircuitBreakerManager:
    """Circuit Breaker Intelligence Manager with strict state machine transition validation."""

    VALID_TRANSITIONS = {
        CircuitBreakerState.CLOSED: {CircuitBreakerState.OPEN},
        CircuitBreakerState.OPEN: {CircuitBreakerState.HALF_OPEN},
        CircuitBreakerState.HALF_OPEN: {CircuitBreakerState.CLOSED, CircuitBreakerState.OPEN},
    }

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._breakers: Dict[str, CircuitBreakerPolicy] = {}

    def get_or_create_breaker(self, tenant_id: str, target_service_id: str) -> CircuitBreakerPolicy:
        key = f"{tenant_id}:{target_service_id}"
        if key not in self._breakers:
            self._breakers[key] = CircuitBreakerPolicy(tenant_id=tenant_id, target_service_id=target_service_id)
        return self._breakers[key]

    def record_failure(self, tenant_id: str, target_service_id: str) -> CircuitBreakerPolicy:
        cb = self.get_or_create_breaker(tenant_id, target_service_id)
        cb.consecutive_failures += 1

        if cb.state == CircuitBreakerState.CLOSED and cb.consecutive_failures >= cb.failure_threshold:
            self.transition_state(cb, CircuitBreakerState.OPEN, "Failure threshold reached")
        elif cb.state == CircuitBreakerState.HALF_OPEN:
            self.transition_state(cb, CircuitBreakerState.OPEN, "Failure during half-open trial")

        return cb

    def record_success(self, tenant_id: str, target_service_id: str) -> CircuitBreakerPolicy:
        cb = self.get_or_create_breaker(tenant_id, target_service_id)
        cb.consecutive_failures = 0

        if cb.state == CircuitBreakerState.HALF_OPEN:
            self.transition_state(cb, CircuitBreakerState.CLOSED, "Successful call during half-open state")

        return cb

    def transition_state(self, breaker: CircuitBreakerPolicy, target_state: CircuitBreakerState, reason: str) -> None:
        current = breaker.state
        if target_state not in self.VALID_TRANSITIONS.get(current, set()):
            raise InvalidFailoverTransitionException(current.value, target_state.value)

        breaker.state = target_state
        breaker.updated_at = datetime.now(timezone.utc)

    def evaluate_circuit_breaker(self, tenant_id: str, target_service_id: str) -> CircuitBreakerAssessment:
        cb = self.get_or_create_breaker(tenant_id, target_service_id)

        if cb.state == CircuitBreakerState.OPEN:
            # Check if recovery time elapsed -> move to HALF_OPEN
            elapsed = (datetime.now(timezone.utc) - cb.updated_at).total_seconds()
            if elapsed >= cb.recovery_time_seconds:
                self.transition_state(cb, CircuitBreakerState.HALF_OPEN, "Recovery timeout elapsed")

        is_allowed = cb.state in (CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN)
        return CircuitBreakerAssessment(
            breaker_id=cb.breaker_id,
            tenant_id=tenant_id,
            target_service_id=target_service_id,
            state=cb.state,
            is_call_allowed=is_allowed,
        )
