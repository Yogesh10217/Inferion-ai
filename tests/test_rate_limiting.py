import pytest
import asyncio
from app.limits.memory_backend import MemoryCounterBackend
from app.limits.rate_limit_service import RateLimitService
from app.limits.exceptions import RateLimitExceededException
from app.services.metrics_service import MetricsService

@pytest.fixture
def metrics():
    return MetricsService()

@pytest.fixture
def memory_backend():
    return MemoryCounterBackend()

@pytest.fixture
def rate_limit_service(memory_backend, metrics):
    return RateLimitService(backend=memory_backend, metrics=metrics)

@pytest.mark.asyncio
async def test_sliding_window_rate_limit(rate_limit_service):
    scope = "test_sliding"
    limit = 2
    window = 1

    await rate_limit_service.check_rate_limit(scope, limit, window, strategy="sliding_window")
    await rate_limit_service.check_rate_limit(scope, limit, window, strategy="sliding_window")

    with pytest.raises(RateLimitExceededException):
        await rate_limit_service.check_rate_limit(scope, limit, window, strategy="sliding_window")

    await asyncio.sleep(1.1)
    
    # Should be allowed again after window expires
    await rate_limit_service.check_rate_limit(scope, limit, window, strategy="sliding_window")

@pytest.mark.asyncio
async def test_token_bucket_rate_limit(rate_limit_service):
    scope = "test_token"
    capacity = 2
    refill_time = 1

    await rate_limit_service.check_rate_limit(scope, capacity, refill_time, strategy="token_bucket")
    await rate_limit_service.check_rate_limit(scope, capacity, refill_time, strategy="token_bucket")

    with pytest.raises(RateLimitExceededException):
        await rate_limit_service.check_rate_limit(scope, capacity, refill_time, strategy="token_bucket")

@pytest.mark.asyncio
async def test_concurrency_leases(rate_limit_service):
    scope = "test_concurrency"
    limit = 1
    
    lease_id = await rate_limit_service.acquire_concurrency_lease(scope, limit)
    assert lease_id is not None
    
    with pytest.raises(RateLimitExceededException):
        await rate_limit_service.acquire_concurrency_lease(scope, limit)
        
    await rate_limit_service.release_concurrency_lease(scope, lease_id)
    
    # Should be allowed again after release
    lease_id2 = await rate_limit_service.acquire_concurrency_lease(scope, limit)
    assert lease_id2 is not None
