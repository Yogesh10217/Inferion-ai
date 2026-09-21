import pytest

from app.cache.memory_backend import MemoryCacheBackend
from app.cache.redis_backend import RedisCacheBackend
from app.knowledge.embedding_service import EmbeddingCache
from app.mlops.registry import AIAssetRegistry, AIAssetStatus, AIAssetType
from app.registry.db_registry import DatabaseModelRegistry
from app.registry.model_metadata import ModelMetadata


@pytest.mark.asyncio
async def test_database_model_registry_crud(get_client):
    registry = DatabaseModelRegistry()
    await registry.load_from_db()

    # Initial seeded models
    assert registry.model_exists("gpt-4o-mini") is True
    assert registry.model_exists("llama3.1") is True

    # Register new model
    new_model = ModelMetadata(
        id="claude-3-5-sonnet",
        provider="anthropic",
        description="Anthropic Claude 3.5 Sonnet",
        context_window=200000,
        status="available",
    )
    registry.register_model(new_model)
    assert registry.get_model("claude-3-5-sonnet") is not None
    assert registry.get_model("claude-3-5-sonnet").provider == "anthropic"

    # Update model
    updated = registry.update_model("claude-3-5-sonnet", {"status": "deprecated"})
    assert updated.status == "deprecated"

    # Remove model
    registry.remove_model("claude-3-5-sonnet")
    assert registry.get_model("claude-3-5-sonnet") is None


@pytest.mark.asyncio
async def test_mlops_ai_asset_registry_persistence():
    registry = AIAssetRegistry()
    asset = registry.register_asset(
        name="Customer Support Agent Prompt",
        asset_type=AIAssetType.PROMPT,
        description="Prompt template for customer support",
        initial_configuration={"system_prompt": "You are a helpful customer support agent."},
    )

    assert asset.name == "Customer Support Agent Prompt"
    assert asset.current_version == "1.0.0"

    # Create new version
    ver2 = registry.create_version(
        asset_id=asset.asset_id,
        version_number="1.1.0",
        configuration={"system_prompt": "You are an expert support agent."},
        changelog="Improved tone and clarity",
    )
    assert ver2.version_number == "1.1.0"
    assert asset.current_version == "1.1.0"

    # Promote to production
    promoted = registry.promote_version(asset.asset_id, "1.1.0", AIAssetStatus.PRODUCTION)
    assert promoted.status == AIAssetStatus.PRODUCTION
    assert promoted.is_immutable is True

    # Rollback version
    rolled_back = registry.rollback_version(asset.asset_id, "1.0.0")
    assert rolled_back.version_number == "1.0.0"


@pytest.mark.asyncio
async def test_memory_cache_backend_lru_eviction():
    # Cache with max capacity 3
    cache = MemoryCacheBackend(max_size=3)

    await cache.set("k1", "v1", ttl_seconds=60)
    await cache.set("k2", "v2", ttl_seconds=60)
    await cache.set("k3", "v3", ttl_seconds=60)

    # Access k1 to make it most recently used (LRU order becomes k2, k3, k1)
    assert await cache.get("k1") == "v1"

    # Add k4 -> should evict k2 (oldest LRU item)
    await cache.set("k4", "v4", ttl_seconds=60)

    assert await cache.get("k2") is None
    assert await cache.get("k1") == "v1"
    assert await cache.get("k3") == "v3"
    assert await cache.get("k4") == "v4"


@pytest.mark.asyncio
async def test_embedding_cache_lru_eviction():
    emb_cache = EmbeddingCache(max_size=2)
    emb_cache.set("text1", [0.1, 0.2])
    emb_cache.set("text2", [0.3, 0.4])

    # Touch text1 so text2 becomes LRU candidate
    assert emb_cache.get("text1") == [0.1, 0.2]

    emb_cache.set("text3", [0.5, 0.6])

    assert emb_cache.get("text2") is None
    assert emb_cache.get("text1") == [0.1, 0.2]
    assert emb_cache.get("text3") == [0.5, 0.6]


@pytest.mark.asyncio
async def test_redis_cache_backend_fallback():
    # Invalid Redis URL should act as graceful no-op without raising unhandled exceptions
    redis_backend = RedisCacheBackend(redis_url="redis://invalid_host:6379/0", max_retries=1)

    assert await redis_backend.get("test_key") is None
    await redis_backend.set("test_key", "val", ttl_seconds=10)
    assert await redis_backend.exists("test_key") is False
