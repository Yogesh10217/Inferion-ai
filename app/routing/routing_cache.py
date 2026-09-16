import threading
import time
from typing import Any, Dict, Optional


class CacheItem:
    def __init__(self, value: Any, ttl_seconds: float):
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class RoutingCache:
    """Thread-safe multi-tier cache for health, metrics, and routing decisions."""

    def __init__(
        self,
        default_ttl: float = 60.0,
        health_ttl: float = 10.0,
        metrics_ttl: float = 30.0,
        decision_ttl: float = 5.0,
    ):
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        self.health_ttl = health_ttl
        self.metrics_ttl = metrics_ttl
        self.decision_ttl = decision_ttl

        self.health_cache: Dict[str, CacheItem] = {}
        self.metrics_cache: Dict[str, CacheItem] = {}
        self.decisions_cache: Dict[str, CacheItem] = {}

        self._hits = 0
        self._misses = 0
        self._evictions = 0

    # --- Health Cache ---
    def set_health(self, provider_id: str, is_healthy: bool, ttl: Optional[float] = None) -> None:
        with self._lock:
            self.health_cache[provider_id] = CacheItem(is_healthy, ttl or self.health_ttl)

    def get_health(self, provider_id: str) -> Optional[bool]:
        with self._lock:
            item = self.health_cache.get(provider_id)
            if not item:
                self._misses += 1
                return None
            if item.is_expired():
                del self.health_cache[provider_id]
                self._evictions += 1
                self._misses += 1
                return None
            self._hits += 1
            return item.value

    # --- Metrics Cache ---
    def set_metrics(self, provider_id: str, stats: Dict[str, Any], ttl: Optional[float] = None) -> None:
        with self._lock:
            self.metrics_cache[provider_id] = CacheItem(stats, ttl or self.metrics_ttl)

    def get_metrics(self, provider_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            item = self.metrics_cache.get(provider_id)
            if not item:
                self._misses += 1
                return None
            if item.is_expired():
                del self.metrics_cache[provider_id]
                self._evictions += 1
                self._misses += 1
                return None
            self._hits += 1
            return item.value

    # --- Decisions Cache ---
    def set_decision(self, cache_key: str, provider_id: str, ttl: Optional[float] = None) -> None:
        with self._lock:
            self.decisions_cache[cache_key] = CacheItem(provider_id, ttl or self.decision_ttl)

    def get_decision(self, cache_key: str) -> Optional[str]:
        with self._lock:
            item = self.decisions_cache.get(cache_key)
            if not item:
                self._misses += 1
                return None
            if item.is_expired():
                del self.decisions_cache[cache_key]
                self._evictions += 1
                self._misses += 1
                return None
            self._hits += 1
            return item.value

    def invalidate_all(self) -> None:
        """Clear all cache tiers."""
        with self._lock:
            self.health_cache.clear()
            self.metrics_cache.clear()
            self.decisions_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Return cache hit/miss statistics and active sizes."""
        with self._lock:
            total_lookups = self._hits + self._misses
            hit_rate = (self._hits / total_lookups) if total_lookups > 0 else 0.0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": round(hit_rate, 4),
                "health_cache_size": len(self.health_cache),
                "metrics_cache_size": len(self.metrics_cache),
                "decisions_cache_size": len(self.decisions_cache),
            }
