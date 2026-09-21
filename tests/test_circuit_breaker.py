import time

import pytest

from app.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException,
    CircuitBreakerPolicy,
    CircuitState,
)


def test_circuit_breaker_initial_state():
    cb = CircuitBreaker("test-cb", CircuitBreakerPolicy(failure_threshold=3, recovery_timeout_seconds=5.0))
    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True


def test_circuit_breaker_opens_after_threshold_failures():
    policy = CircuitBreakerPolicy(failure_threshold=3, recovery_timeout_seconds=10.0)
    cb = CircuitBreaker("test-cb", policy)

    cb.record_failure(Exception("Err 1"))
    assert cb.state == CircuitState.CLOSED

    cb.record_failure(Exception("Err 2"))
    assert cb.state == CircuitState.CLOSED

    # 3rd failure opens circuit
    cb.record_failure(Exception("Err 3"))
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False


def test_circuit_breaker_half_open_transition():
    policy = CircuitBreakerPolicy(failure_threshold=2, recovery_timeout_seconds=1.0)
    cb = CircuitBreaker("test-cb", policy)

    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Force last failure time in past
    cb.last_failure_time = time.time() - 2.0

    # allow_request should transition to HALF_OPEN
    assert cb.allow_request() is True
    assert cb.state == CircuitState.HALF_OPEN


def test_circuit_breaker_recloses_after_successes_in_half_open():
    policy = CircuitBreakerPolicy(failure_threshold=2, recovery_timeout_seconds=1.0, success_threshold=2)
    cb = CircuitBreaker("test-cb", policy)

    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    cb.last_failure_time = time.time() - 2.0
    cb.allow_request()  # Transitions to HALF_OPEN

    cb.record_success()
    assert cb.state == CircuitState.HALF_OPEN  # Needs 2 successes

    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_call_async_wrapper():
    policy = CircuitBreakerPolicy(failure_threshold=2, recovery_timeout_seconds=5.0)
    cb = CircuitBreaker("test-cb", policy)

    async def successful_fn(x: int):
        return x * 2

    res = await cb.call_async(successful_fn, 5)
    assert res == 10

    async def failing_fn():
        raise ValueError("Backend failed")

    # Fail twice
    with pytest.raises(ValueError):
        await cb.call_async(failing_fn)
    with pytest.raises(ValueError):
        await cb.call_async(failing_fn)

    # Circuit should now be open -> subsequent call raises CircuitBreakerOpenException
    with pytest.raises(CircuitBreakerOpenException) as exc_info:
        await cb.call_async(successful_fn, 5)

    assert "test-cb" in str(exc_info.value)
