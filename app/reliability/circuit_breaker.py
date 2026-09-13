"""
Phase 5.70 - Circuit Breaker Module.

Canonical CircuitBreaker state machine implementation (CLOSED, OPEN, HALF_OPEN) with failure tracking and illegal transition protection.
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class CircuitBreakerState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreakerResult:
    name: str
    state: CircuitBreakerState
    failure_count: int
    success_count: int
    failure_threshold: int
    recovery_timeout_seconds: float
    state_changed: bool
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """Manages failure threshold tracking and state transitions for downstream service calls."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.evidence_level = evidence_level

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_state_change = time.time()
        self._history: List[Dict[str, Any]] = []

    @property
    def state(self) -> CircuitBreakerState:
        # Check if OPEN timeout has elapsed -> transition to HALF_OPEN
        if self._state == CircuitBreakerState.OPEN:
            if time.time() - self._last_state_change >= self.recovery_timeout_seconds:
                self._transition_to(CircuitBreakerState.HALF_OPEN, reason="Recovery timeout elapsed")
        return self._state

    def record_success(self) -> CircuitBreakerResult:
        old_state = self._state
        self._success_count += 1

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._failure_count = 0
            self._transition_to(CircuitBreakerState.CLOSED, reason="Successful call in HALF_OPEN state")

        return CircuitBreakerResult(
            name=self.name,
            state=self._state,
            failure_count=self._failure_count,
            success_count=self._success_count,
            failure_threshold=self.failure_threshold,
            recovery_timeout_seconds=self.recovery_timeout_seconds,
            state_changed=(self._state != old_state),
            evidence_level=self.evidence_level,
        )

    def record_failure(self) -> CircuitBreakerResult:
        old_state = self._state
        self._failure_count += 1

        if self._state == CircuitBreakerState.CLOSED and self._failure_count >= self.failure_threshold:
            self._transition_to(CircuitBreakerState.OPEN, reason=f"Failure threshold ({self.failure_threshold}) reached")
        elif self._state == CircuitBreakerState.HALF_OPEN:
            self._transition_to(CircuitBreakerState.OPEN, reason="Failure recorded during HALF_OPEN probe")

        return CircuitBreakerResult(
            name=self.name,
            state=self._state,
            failure_count=self._failure_count,
            success_count=self._success_count,
            failure_threshold=self.failure_threshold,
            recovery_timeout_seconds=self.recovery_timeout_seconds,
            state_changed=(self._state != old_state),
            evidence_level=self.evidence_level,
        )

    def _transition_to(self, target_state: CircuitBreakerState, reason: str) -> None:
        now = time.time()
        self._history.append({
            "from_state": self._state.value,
            "to_state": target_state.value,
            "reason": reason,
            "timestamp": now,
        })
        self._state = target_state
        self._last_state_change = now
