"""Unit tests for RateLimiter."""

from app.governance.rate_limiter import RateLimitAlgorithm, RateLimiter, RateLimitPolicy


def test_sliding_window_rate_limiter():
    limiter = RateLimiter()
    policy = RateLimitPolicy(
        key_prefix="test_sw", max_requests=2, window_seconds=10, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
    )

    res1 = limiter.consume(policy, tenant_id="t1")
    assert res1.allowed is True
    assert res1.remaining == 1

    res2 = limiter.consume(policy, tenant_id="t1")
    assert res2.allowed is True
    assert res2.remaining == 0

    res3 = limiter.consume(policy, tenant_id="t1")
    assert res3.allowed is False
    assert res3.retry_after_seconds > 0.0


def test_token_bucket_rate_limiter():
    limiter = RateLimiter()
    policy = RateLimitPolicy(
        key_prefix="test_tb", max_requests=2, window_seconds=60, algorithm=RateLimitAlgorithm.TOKEN_BUCKET
    )

    res1 = limiter.consume(policy, tenant_id="t2")
    assert res1.allowed is True

    res2 = limiter.consume(policy, tenant_id="t2")
    assert res2.allowed is True

    res3 = limiter.consume(policy, tenant_id="t2")
    assert res3.allowed is False
