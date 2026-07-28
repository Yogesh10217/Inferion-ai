import time
import uuid
import logging
from typing import Tuple, Optional

import redis.asyncio as aioredis
from redis.exceptions import RedisError

from app.limits.counter_backend import CounterBackend
from app.limits.memory_backend import MemoryCounterBackend
from app.limits.redis_lua_scripts import (
    SLIDING_WINDOW_LUA,
    TOKEN_BUCKET_LUA,
    FIXED_WINDOW_LUA,
    ACQUIRE_LEASE_LUA
)
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class RedisCounterBackend(CounterBackend):
    """
    Redis-backed rate limiting with circuit breaker to memory fallback.
    Executes atomic Lua scripts.
    """
    def __init__(self, redis_url: str, metrics: MetricsService):
        self.redis_url = redis_url
        self.metrics = metrics
        self.redis: Optional[aioredis.Redis] = None
        self.fallback = MemoryCounterBackend()
        
        self.fallback_active = False
        self.last_fallback_time = 0.0
        self.fallback_duration = 30.0  # Retry Redis after 30s
        
        # Pre-loaded scripts
        self._script_sliding: Optional[aioredis.client.Script] = None
        self._script_token: Optional[aioredis.client.Script] = None
        self._script_fixed: Optional[aioredis.client.Script] = None
        self._script_lease: Optional[aioredis.client.Script] = None

    async def _get_redis(self) -> Optional[aioredis.Redis]:
        if self.fallback_active:
            if time.time() - self.last_fallback_time > self.fallback_duration:
                # Attempt to recover
                logger.info("Attempting to recover Redis connection for rate limits")
                self.fallback_active = False
            else:
                return None
                
        if self.redis is None:
            try:
                self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
                self._script_sliding = self.redis.register_script(SLIDING_WINDOW_LUA)
                self._script_token = self.redis.register_script(TOKEN_BUCKET_LUA)
                self._script_fixed = self.redis.register_script(FIXED_WINDOW_LUA)
                self._script_lease = self.redis.register_script(ACQUIRE_LEASE_LUA)
            except RedisError as e:
                self._trigger_fallback(e)
                return None
                
        return self.redis

    def _trigger_fallback(self, exc: Exception) -> None:
        if not self.fallback_active:
            logger.error(f"Redis rate limiting failed, falling back to memory: {exc}")
            self.metrics.record_redis_fallback()
            self.fallback_active = True
            self.last_fallback_time = time.time()
            self.redis = None

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    async def check_and_increment_sliding_window(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        redis_client = await self._get_redis()
        if redis_client is None:
            return await self.fallback.check_and_increment_sliding_window(key, limit, window_seconds)
            
        try:
            res = await self._script_sliding(keys=[key], args=[self._now_ms(), window_seconds * 1000, limit])
            return res[0] == 1, res[1]
        except RedisError as e:
            self._trigger_fallback(e)
            return await self.fallback.check_and_increment_sliding_window(key, limit, window_seconds)

    async def check_and_decrement_token_bucket(self, key: str, capacity: int, refill_time_seconds: int) -> Tuple[bool, int]:
        redis_client = await self._get_redis()
        if redis_client is None:
            return await self.fallback.check_and_decrement_token_bucket(key, capacity, refill_time_seconds)
            
        try:
            tokens_key = f"{key}:tokens"
            ts_key = f"{key}:ts"
            res = await self._script_token(
                keys=[tokens_key, ts_key], 
                args=[capacity, refill_time_seconds * 1000, 1, self._now_ms()]
            )
            return res[0] == 1, res[1]
        except RedisError as e:
            self._trigger_fallback(e)
            return await self.fallback.check_and_decrement_token_bucket(key, capacity, refill_time_seconds)

    async def check_and_increment_fixed_window(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        redis_client = await self._get_redis()
        if redis_client is None:
            return await self.fallback.check_and_increment_fixed_window(key, limit, window_seconds)
            
        try:
            res = await self._script_fixed(keys=[key], args=[limit, window_seconds])
            return res[0] == 1, res[1]
        except RedisError as e:
            self._trigger_fallback(e)
            return await self.fallback.check_and_increment_fixed_window(key, limit, window_seconds)

    async def acquire_lease(self, scope_key: str, limit: int, ttl_seconds: int) -> Tuple[bool, str]:
        redis_client = await self._get_redis()
        if redis_client is None:
            return await self.fallback.acquire_lease(scope_key, limit, ttl_seconds)
            
        try:
            lease_id = str(uuid.uuid4())
            res = await self._script_lease(keys=[scope_key], args=[limit, ttl_seconds, lease_id, self._now_ms()])
            return res[0] == 1, res[1]
        except RedisError as e:
            self._trigger_fallback(e)
            return await self.fallback.acquire_lease(scope_key, limit, ttl_seconds)

    async def release_lease(self, scope_key: str, lease_id: str) -> None:
        redis_client = await self._get_redis()
        if redis_client is None:
            await self.fallback.release_lease(scope_key, lease_id)
            return
            
        try:
            await redis_client.hdel(scope_key, lease_id)
        except RedisError:
            pass  # It will expire automatically anyway
