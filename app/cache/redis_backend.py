import logging
from typing import Any, Optional

from app.cache.cache_backend import BaseCacheBackend

logger = logging.getLogger("app.cache.redis_backend")

try:
    import redis.asyncio as redis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore


class RedisCacheBackend(BaseCacheBackend):
    """Redis-based cache backend. Fails gracefully if Redis is unavailable."""

    def __init__(self, redis_url: str):
        if not REDIS_AVAILABLE:
            logger.warning("Redis is not installed. RedisCacheBackend will act as a no-op.")
            self._client = None
        else:
            try:
                self._client = redis.from_url(redis_url, decode_responses=True)
            except Exception as exc:
                logger.error(f"Failed to initialize Redis client: {exc}")
                self._client = None

    async def get(self, key: str) -> Optional[Any]:
        if not self._client:
            return None
        try:
            value = await self._client.get(key)
            return value
        except Exception as exc:
            logger.error(f"Redis get failed for key {key}: {exc}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if not self._client:
            return
        try:
            await self._client.setex(key, ttl_seconds, value)
        except Exception as exc:
            logger.error(f"Redis set failed for key {key}: {exc}")

    async def delete(self, key: str) -> bool:
        if not self._client:
            return False
        try:
            result = await self._client.delete(key)
            return bool(result)
        except Exception as exc:
            logger.error(f"Redis delete failed for key {key}: {exc}")
            return False

    async def exists(self, key: str) -> bool:
        if not self._client:
            return False
        try:
            result = await self._client.exists(key)
            return bool(result)
        except Exception as exc:
            logger.error(f"Redis exists failed for key {key}: {exc}")
            return False

    async def clear(self) -> None:
        if not self._client:
            return
        try:
            await self._client.flushdb()
        except Exception as exc:
            logger.error(f"Redis clear failed: {exc}")
