"""Enterprise Circuit Breaker Pattern Implementation."""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel, Field

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, fast reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery with limited requests


class CircuitBreakerPolicy(BaseModel):
    """Configuration rules for circuit breaker behavior."""

    failure_threshold: int = 5          # Consecutive or total failures to open
    recovery_timeout_seconds: float = 30.0  # Time in OPEN before going HALF_OPEN
    success_threshold: int = 2          # Consecutive successes in HALF_OPEN to close
    allowed_exceptions: list = Field(default_factory=list)


class CircuitBreakerOpenException(AppException):
    """Raised when call is blocked because circuit breaker is OPEN."""

    def __init__(self, name: str, recovery_in_sec: float) -> None:
        super().__init__(
            message=f"Circuit breaker '{name}' is OPEN. Retrying in {recovery_in_sec:.1f}s",
            code="CIRCUIT_BREAKER_OPEN",
            status_code=503,
            details={"name": name, "recovery_in_sec": recovery_in_sec},
        )


class CircuitBreaker:
    """Stateful circuit breaker protecting remote components from cascading failures."""

    def __init__(self, name: str, policy: Optional[CircuitBreakerPolicy] = None) -> None:
        self.name = name
        self.policy = policy or CircuitBreakerPolicy()
        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.success_count: int = 0
        self.last_failure_time: float = 0.0
        self.last_state_change_time: float = time.time()

    def _update_state(self, new_state: CircuitState) -> None:
        if self.state != new_state:
            logger.warning(f"[CIRCUIT BREAKER] '{self.name}' state transition: {self.state.value} -> {new_state.value}")
            self.state = new_state
            self.last_state_change_time = time.time()

    def allow_request(self) -> bool:
        """Check if request is permitted under current circuit state."""
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if now - self.last_failure_time >= self.policy.recovery_timeout_seconds:
                self._update_state(CircuitState.HALF_OPEN)
                self.success_count = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def record_success(self) -> None:
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.policy.success_threshold:
                self.failure_count = 0
                self._update_state(CircuitState.CLOSED)
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self, exception: Optional[Exception] = None) -> None:
        """Record failed execution."""
        self.last_failure_time = time.time()
        self.failure_count += 1

        if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            if self.failure_count >= self.policy.failure_threshold:
                self._update_state(CircuitState.OPEN)

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function wrapped by circuit breaker protection."""
        if not self.allow_request():
            rec_sec = max(0.0, self.policy.recovery_timeout_seconds - (time.time() - self.last_failure_time))
            raise CircuitBreakerOpenException(self.name, rec_sec)

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as exc:
            self.record_failure(exc)
            raise


class CircuitBreakerRegistry:
    """Registry maintaining per-provider, per-tool, per-service circuit breakers."""

    def __init__(self) -> None:
        self._breakers: Dict[str, CircuitBreaker] = {}

    def get_breaker(self, name: str, policy: Optional[CircuitBreakerPolicy] = None) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, policy or CircuitBreakerPolicy())
        return self._breakers[name]

    def list_breakers(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "state": cb.state.value,
                "failures": cb.failure_count,
                "successes": cb.success_count,
            }
            for name, cb in self._breakers.items()
        }
