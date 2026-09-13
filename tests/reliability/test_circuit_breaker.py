"""
Tests for Circuit Breaker Module.
"""

import time

from app.reliability.circuit_breaker import CircuitBreaker, CircuitBreakerState


def test_circuit_breaker_state_transitions():
    cb = CircuitBreaker("test_breaker", failure_threshold=2, recovery_timeout_seconds=0.1)
    assert cb.state == CircuitBreakerState.CLOSED

    # Fail attempt 1 -> CLOSED
    cb.record_failure()
    assert cb.state == CircuitBreakerState.CLOSED

    # Fail attempt 2 -> OPEN
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN

    # Sleep recovery timeout -> HALF_OPEN
    time.sleep(0.15)
    assert cb.state == CircuitBreakerState.HALF_OPEN

    # Success in HALF_OPEN -> CLOSED
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED
