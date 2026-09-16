from typing import Any

from app.services.batching.batch_entry import QueueEntry


class CachePolicy:
    """Centralized rules for determining cacheability of requests and responses."""

    def __init__(self, ttl_seconds: int = 3600, no_cache: bool = False):
        self.ttl_seconds = ttl_seconds
        self.no_cache = no_cache
        self.write_through = True
        self.read_through = True

    def is_request_cacheable(self, entry: QueueEntry) -> bool:
        """Check if an incoming request can be served from cache."""
        if self.no_cache or not self.read_through:
            return False

        if entry.is_streaming:
            return False

        if entry.cancellation_state.is_set():
            return False

        return True

    def is_response_cacheable(self, entry: QueueEntry, response: Any) -> bool:
        """Check if a response should be stored in the cache."""
        if self.no_cache or not self.write_through:
            return False

        if entry.is_streaming:
            return False

        if entry.cancellation_state.is_set():
            return False

        if isinstance(response, Exception):
            return False

        # We don't cache partial or failed responses
        # Assuming inference responses have a status or we only cache success
        # For now, if it's not an Exception, it's successful in our simple model,
        # but we can extend this if InferenceResponse has more fields.
        return True
