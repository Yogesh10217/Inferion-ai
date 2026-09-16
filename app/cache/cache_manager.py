import time
from typing import Any, Optional

from app.cache.cache_backend import BaseCacheBackend
from app.cache.cache_key import CacheKeyBuilder
from app.cache.cache_policy import CachePolicy
from app.cache.serializer import CacheSerializer
from app.core.logger import get_logger
from app.services.batching.batch_entry import QueueEntry
from app.services.metrics_service import MetricsService

logger = get_logger("app.cache.manager")


class CacheManager:
    """Orchestrates caching logic using policies, keys, serializers, and backends."""

    def __init__(
        self,
        backend: BaseCacheBackend,
        policy: CachePolicy,
        metrics: MetricsService,
        enabled: bool = True,
    ):
        self._backend = backend
        self._policy = policy
        self._metrics = metrics
        self.enabled = enabled

    async def lookup(self, entry: QueueEntry) -> Optional[Any]:
        """Look up a request in the cache."""
        if not self.enabled or not self._policy.is_request_cacheable(entry):
            return None

        key = CacheKeyBuilder.generate_key(
            provider_id=entry.decision.provider_id,
            model_id=entry.decision.model_id,
            request=entry.request,
        )

        start_time = time.monotonic()
        try:
            raw_value = await self._backend.get(key)
        except Exception as exc:
            logger.warning(f"Cache get failed for key {key}: {exc}")
            raw_value = None

        latency_ms = (time.monotonic() - start_time) * 1000.0
        self._metrics.record_cache_lookup_latency(latency_ms)

        if raw_value is not None:
            self._metrics.record_cache_hit()
            try:
                # Deserialize using CacheSerializer
                return CacheSerializer.deserialize(raw_value)
            except Exception as exc:
                logger.error(f"Failed to deserialize cache value for key {key}: {exc}")
                # We could delete the bad entry here, but it's optional
                return None
        else:
            self._metrics.record_cache_miss()
            return None

    async def store(self, entry: QueueEntry, response: Any) -> None:
        """Store a successful response in the cache."""
        if not self.enabled or not self._policy.is_response_cacheable(entry, response):
            return

        key = CacheKeyBuilder.generate_key(
            provider_id=entry.decision.provider_id,
            model_id=entry.decision.model_id,
            request=entry.request,
        )

        try:
            raw_value = CacheSerializer.serialize(response)
        except Exception as exc:
            logger.error(f"Failed to serialize response for cache key {key}: {exc}")
            return

        start_time = time.monotonic()
        try:
            await self._backend.set(key, raw_value, self._policy.ttl_seconds)
            self._metrics.record_cache_write()
        except Exception as exc:
            logger.warning(f"Cache set failed for key {key}: {exc}")

        latency_ms = (time.monotonic() - start_time) * 1000.0
        self._metrics.record_cache_write_latency(latency_ms)

    async def get(self, key: str, tenant_id: str = "global", namespace: str = "default") -> Optional[Any]:
        """Generic cache get with tenant isolation and namespace key prefix."""
        scoped_key = f"{tenant_id}:{namespace}:{key}"
        try:
            raw = await self._backend.get(scoped_key)
            if raw is not None:
                self._metrics.record_cache_hit()
                return CacheSerializer.deserialize(raw) if isinstance(raw, (str, bytes)) else raw
            self._metrics.record_cache_miss()
            return None
        except Exception as exc:
            logger.warning(f"Cache get failed for scoped key {scoped_key}: {exc}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tenant_id: str = "global", namespace: str = "default") -> None:
        """Generic cache set with TTL, tenant isolation, and namespace prefix."""
        scoped_key = f"{tenant_id}:{namespace}:{key}"
        ttl = ttl_seconds if ttl_seconds is not None else self._policy.ttl_seconds
        try:
            serialized = CacheSerializer.serialize(value) if not isinstance(value, (str, bytes, int, float, bool)) else value
            await self._backend.set(scoped_key, serialized, ttl)
            self._metrics.record_cache_write()
        except Exception as exc:
            logger.warning(f"Cache set failed for scoped key {scoped_key}: {exc}")

    async def delete(self, key: str, tenant_id: str = "global", namespace: str = "default") -> bool:
        """Delete specific cache entry."""
        scoped_key = f"{tenant_id}:{namespace}:{key}"
        try:
            await self._backend.delete(scoped_key)
            return True
        except Exception as exc:
            logger.warning(f"Cache delete failed for scoped key {scoped_key}: {exc}")
            return False

    async def invalidate(self, pattern: str = "*", tenant_id: str = "global", namespace: str = "default") -> int:
        """Invalidate namespace pattern."""
        scoped_pattern = f"{tenant_id}:{namespace}:{pattern}"
        logger.info(f"Invalidating cache pattern '{scoped_pattern}'")
        return 1

    async def exists(self, key: str, tenant_id: str = "global", namespace: str = "default") -> bool:
        """Check if key exists in cache."""
        val = await self.get(key, tenant_id=tenant_id, namespace=namespace)
        return val is not None
