"""Distributed Lock Manager with Owner & Lease Expiration Safety."""

import time
import logging
import asyncio
import uuid
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DistributedLock:
    """Lock instance acquired by a specific owner with TTL expiration."""

    def __init__(self, key: str, owner_id: str, lease_seconds: float) -> None:
        self.key = key
        self.owner_id = owner_id
        self.lease_seconds = lease_seconds
        self.acquired_at = time.time()

    @property
    def expires_at(self) -> float:
        return self.acquired_at + self.lease_seconds

    def is_valid(self) -> bool:
        return time.time() < self.expires_at


class DistributedLockManager:
    """Manages distributed locks preventing duplicate job/workflow execution and coordinating leader election."""

    def __init__(self) -> None:
        self._locks: Dict[str, DistributedLock] = {}

    async def acquire_lock(
        self,
        key: str,
        owner_id: Optional[str] = None,
        ttl_seconds: float = 30.0,
    ) -> Optional[DistributedLock]:
        """Try to acquire a lock for a given key."""
        now = time.time()
        owner = owner_id or f"owner_{uuid.uuid4().hex[:8]}"

        if key in self._locks:
            current_lock = self._locks[key]
            if current_lock.is_valid():
                # Lock held by someone else and still valid
                if current_lock.owner_id == owner:
                    # Re-acquire/extend
                    current_lock.acquired_at = now
                    current_lock.lease_seconds = ttl_seconds
                    return current_lock
                return None
            else:
                logger.info(f"[DISTRIBUTED LOCK] Expired lock '{key}' cleaned up")

        # Lock is available or expired
        lock = DistributedLock(key=key, owner_id=owner, lease_seconds=ttl_seconds)
        self._locks[key] = lock
        logger.info(f"[DISTRIBUTED LOCK] Acquired lock '{key}' by '{owner}' (ttl: {ttl_seconds}s)")
        return lock

    async def release_lock(self, key: str, owner_id: str) -> bool:
        """Release lock if owner matches."""
        if key not in self._locks:
            return False

        lock = self._locks[key]
        if lock.owner_id == owner_id or not lock.is_valid():
            del self._locks[key]
            logger.info(f"[DISTRIBUTED LOCK] Released lock '{key}' by '{owner_id}'")
            return True

        logger.warning(f"[DISTRIBUTED LOCK] Release failed: owner mismatch for '{key}'")
        return False

    async def is_locked(self, key: str) -> bool:
        """Check if lock is active and valid."""
        if key not in self._locks:
            return False
        return self._locks[key].is_valid()
