"""
Agent Planning & Tool Execution Caching Engine
"""

import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AgentCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def _hash_key(self, namespace: str, key_data: Any) -> str:
        serialized = json.dumps(key_data, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return f"{namespace}:{digest}"

    def get(self, namespace: str, key_data: Any) -> Optional[Any]:
        key = self._hash_key(namespace, key_data)
        item = self._store.get(key)
        if not item:
            return None
        if time.time() > item["expires_at"]:
            del self._store[key]
            return None
        logger.debug(f"Cache hit for namespace '{namespace}'")
        return item["value"]

    def set(self, namespace: str, key_data: Any, value: Any, ttl: Optional[int] = None) -> None:
        key = self._hash_key(namespace, key_data)
        effective_ttl = ttl if ttl is not None else self.ttl_seconds
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + effective_ttl
        }
        logger.debug(f"Cache stored for namespace '{namespace}'")

    def clear(self) -> None:
        self._store.clear()
