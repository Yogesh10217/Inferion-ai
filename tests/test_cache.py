import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.cache.cache_key import CacheKeyBuilder
from app.cache.cache_manager import CacheManager
from app.cache.cache_policy import CachePolicy
from app.cache.memory_backend import MemoryCacheBackend
from app.cache.serializer import CacheSerializer
from app.routing.request_router import RoutingDecision
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import InferenceRequest
from app.services.batching.batch_entry import QueueEntry
from app.services.metrics_service import MetricsService

# Re-enable if Redis is installed/mocked
from app.cache.redis_backend import RedisCacheBackend


@pytest.fixture
def mock_request():
    return InferenceRequest(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7,
        top_p=1.0,
    )


@pytest.fixture
def mock_response():
    return InferenceResponse(
        id="test-id",
        model="gpt-4o-mini",
        provider="openai",
        text="Hello there",
        usage=Usage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
    )


def test_cache_key_generation(mock_request):
    key1 = CacheKeyBuilder.generate_key("openai", "gpt-4o-mini", mock_request)
    
    # Generate again, should be identical
    key2 = CacheKeyBuilder.generate_key("openai", "gpt-4o-mini", mock_request)
    assert key1 == key2
    assert key1.startswith("v1:openai:gpt-4o-mini:")
    
    # Change request slightly
    mock_request.temperature = 0.8
    key3 = CacheKeyBuilder.generate_key("openai", "gpt-4o-mini", mock_request)
    assert key1 != key3


@pytest.mark.asyncio
async def test_memory_backend_ttl():
    backend = MemoryCacheBackend()
    
    await backend.set("test-key", "value", ttl_seconds=1)
    assert await backend.get("test-key") == "value"
    assert await backend.exists("test-key") is True
    
    await asyncio.sleep(1.1)
    
    assert await backend.get("test-key") is None
    assert await backend.exists("test-key") is False


@pytest.mark.asyncio
async def test_cache_manager_lookup_and_store(mock_request, mock_response):
    decision = RoutingDecision(provider_id="openai", model_id="gpt-4o-mini")
    mock_entry = QueueEntry(
        request=mock_request,
        decision=decision,
        is_streaming=False,
    )
    
    backend = MemoryCacheBackend()
    policy = CachePolicy(ttl_seconds=60)
    metrics = MetricsService()
    
    manager = CacheManager(backend=backend, policy=policy, metrics=metrics)
    
    # Initial lookup should miss
    result = await manager.lookup(mock_entry)
    assert result is None
    assert metrics._cache_misses == 1
    assert metrics._cache_hits == 0
    
    # Store the response
    await manager.store(mock_entry, mock_response)
    assert metrics._cache_writes == 1
    
    # Second lookup should hit
    result2 = await manager.lookup(mock_entry)
    assert result2 is not None
    assert result2.text == "Hello there"
    assert metrics._cache_hits == 1


@pytest.mark.asyncio
async def test_cache_policy_streaming_bypass(mock_request, mock_response):
    decision = RoutingDecision(provider_id="openai", model_id="gpt-4o-mini")
    mock_entry = QueueEntry(
        request=mock_request,
        decision=decision,
        is_streaming=False,
    )
    
    backend = MemoryCacheBackend()
    policy = CachePolicy(ttl_seconds=60)
    metrics = MetricsService()
    
    manager = CacheManager(backend=backend, policy=policy, metrics=metrics)
    
    mock_entry.is_streaming = True
    
    await manager.store(mock_entry, mock_response)
    # Should not write due to stream=True
    assert metrics._cache_writes == 0
    
    result = await manager.lookup(mock_entry)
    assert result is None
    assert metrics._cache_misses == 0 # Lookup exits early before metrics


@pytest.mark.asyncio
async def test_cache_serialization(mock_response):
    serialized = CacheSerializer.serialize(mock_response)
    assert isinstance(serialized, str)
    
    deserialized = CacheSerializer.deserialize(serialized)
    assert deserialized.id == mock_response.id
    assert deserialized.text == mock_response.text
    assert deserialized.usage.total_tokens == 20


@pytest.mark.asyncio
async def test_redis_backend_graceful_failover():
    # If redis isn't installed or mock is used, it shouldn't crash
    with patch("app.cache.redis_backend.logger") as mock_logger:
        backend = RedisCacheBackend(redis_url="redis://invalid")
        
        # Test basic ops don't crash
        await backend.set("test", "value", 60)
        res = await backend.get("test")
        assert res is None
        assert await backend.exists("test") is False
        await backend.delete("test")
        await backend.clear()
