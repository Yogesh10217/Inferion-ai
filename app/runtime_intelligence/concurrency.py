"""Runtime Concurrency Manager for Phase 5.57 Runtime Intelligence."""

import logging
import threading
from typing import Set
from app.runtime_intelligence.exceptions import RuntimeConcurrencyConflictException

logger = logging.getLogger(__name__)


class RuntimeConcurrencyManager:
    """Manages thread-safe operation locks to prevent conflicting runtime adaptations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_resources: Set[str] = set()

    def acquire_lock(self, tenant_id: str, resource_id: str) -> str:
        key = f"{tenant_id}:{resource_id}"
        with self._lock:
            if key in self._active_resources:
                logger.warning(f"Concurrency conflict for key '{key}'")
                raise RuntimeConcurrencyConflictException(resource_id)
            self._active_resources.add(key)
            return key

    def release_lock(self, tenant_id: str, resource_id: str) -> None:
        key = f"{tenant_id}:{resource_id}"
        with self._lock:
            self._active_resources.discard(key)
