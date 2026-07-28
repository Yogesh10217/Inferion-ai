from app.events.retry_policy import RetryPolicy


def test_retry_policy_defaults_and_calculation():
    policy = RetryPolicy(
        max_retries=3,
        initial_interval_ms=100,
        max_interval_ms=1000,
        backoff_factor=2.0,
        jitter_ratio=0.0,  # disable jitter for exact testing
    )

    assert policy.should_retry(attempt=1, status_code=500) is True
    assert policy.should_retry(attempt=2, status_code=503) is True
    assert policy.should_retry(attempt=3, status_code=500) is False  # max_retries=3 reached
    assert policy.should_retry(attempt=1, status_code=400) is False  # 400 is non-retryable

    # Delay calculations
    delay_1 = policy.calculate_delay_ms(1)
    delay_2 = policy.calculate_delay_ms(2)

    assert delay_1 == 100.0
    assert delay_2 == 200.0


def test_retry_policy_custom_status_codes():
    policy = RetryPolicy(
        max_retries=4,
        retryable_status_codes=[429, 502],
    )

    assert policy.should_retry(attempt=1, status_code=429) is True
    assert policy.should_retry(attempt=1, status_code=502) is True
    assert policy.should_retry(attempt=1, status_code=500) is False


def test_retry_policy_serialization():
    policy = RetryPolicy(max_retries=10, initial_interval_ms=500)
    data = policy.to_dict()
    restored = RetryPolicy.from_dict(data)

    assert restored.max_retries == 10
    assert restored.initial_interval_ms == 500
