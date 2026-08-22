"""Unit tests for CircuitBreaker."""

import pytest
import asyncio
from app.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerPolicy, CircuitState, CircuitBreakerOpenException


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    policy = CircuitBreakerPolicy(failure_threshold=2, recovery_timeout_seconds=0.2, success_threshold=1)
    cb = CircuitBreaker("test_cb", policy)

    assert cb.state == CircuitState.CLOSED

    # Failure 1
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # Failure 2 -> State transitions to OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Call while OPEN raises exception
    with pytest.raises(CircuitBreakerOpenException):
        await cb.call_async(lambda: "ok")

    # Wait for recovery timeout
    await asyncio.sleep(0.25)

    # State transitions to HALF_OPEN and allows trial call
    async def dummy_success():
        return "success"

    res = await cb.call_async(dummy_success)
    assert res == "success"
    assert cb.state == CircuitState.CLOSED
