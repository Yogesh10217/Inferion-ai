import asyncio
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
    """Production Redis-based cache backend with connection pooling and exponential backoff retry."""

    def __init__(self, redis_url: str, max_connections: int = 20, max_retries: int = 3):
        self.max_retries = max_retries
        if not REDIS_AVAILABLE:
            logger.warning("Redis is not installed. RedisCacheBackend will act as a no-op.")
            self._pool = None
            self._client = None
        else:
            try:
                self._pool = redis.ConnectionPool.from_url(
                    redis_url, max_connections=max_connections, decode_responses=True
                )
                self._client = redis.Redis(connection_pool=self._pool)
            except Exception as exc:
                logger.error(f"Failed to initialize Redis connection pool: {exc}")
                self._pool = None
                self._client = None

    async def _execute_with_retry(self, coro_fn, *args, **kwargs) -> Any:
        if not self._client:
            return None

        backoff_delays = [0.1, 0.2, 0.4]
        for attempt in range(self.max_retries):
            try:
                return await coro_fn(*args, **kwargs)
            except (RedisError, ConnectionError, OSError) as exc:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff_delays[attempt])
                    continue
                logger.error(f"Redis operation failed after {self.max_retries} attempts: {exc}")
                return None
            except Exception as exc:
                logger.error(f"Unexpected error in Redis backend: {exc}")
                return None
        return None

    async def get(self, key: str) -> Optional[Any]:
        if not self._client:
            return None
        return await self._execute_with_retry(self._client.get, key)

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if not self._client:
            return
        await self._execute_with_retry(self._client.setex, key, ttl_seconds, value)

    async def delete(self, key: str) -> bool:
        if not self._client:
            return False
        res = await self._execute_with_retry(self._client.delete, key)
        return bool(res)

    async def exists(self, key: str) -> bool:
        if not self._client:
            return False
        res = await self._execute_with_retry(self._client.exists, key)
        return bool(res)

    async def clear(self) -> None:
        if not self._client:
            return
        await self._execute_with_retry(self._client.flushdb)

    async def close(self) -> None:
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
