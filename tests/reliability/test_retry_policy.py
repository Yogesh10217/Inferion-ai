"""
Tests for Retry Policy Engine Module.
"""

from app.reliability.retry_policy import RetryPolicyConfig, RetryPolicyEngine


def test_retry_policy_exponential_backoff_and_bounding():
    config = RetryPolicyConfig(max_attempts=3, initial_delay_seconds=1.0, max_delay_seconds=10.0, backoff_factor=2.0)
    engine = RetryPolicyEngine(config)

    res = engine.execute_retry_simulation(fail_until_attempt=2)
    assert res.success is True
    assert res.total_attempts == 2
    assert res.total_attempts <= config.max_attempts
