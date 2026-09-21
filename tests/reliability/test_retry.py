"""Unit tests for RetryManager."""

import pytest

from app.resilience.retry import RetryManager, RetryPolicy


@pytest.mark.asyncio
async def test_retry_success_after_failure():
    rm = RetryManager()
    attempts = 0

    async def flaky_func():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ConnectionError("Transient network failure")
        return "success"

    policy = RetryPolicy(max_attempts=3, initial_interval_seconds=0.01)
    res = await rm.execute_async(flaky_func, policy=policy)

    assert res == "success"
    assert attempts == 2
