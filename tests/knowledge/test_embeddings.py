import pytest
from app.knowledge.embedding_service import OpenAIProvider, EmbeddingCache

@pytest.mark.asyncio
async def test_embedding_provider_cache():
    cache = EmbeddingCache()
    cache.set("test_key", [0.1, 0.2, 0.3])
    res = cache.get("test_key")
    assert res == [0.1, 0.2, 0.3]
