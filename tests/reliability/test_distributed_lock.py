"""Unit tests for DistributedLockManager."""

import pytest
from app.cache.distributed_lock import DistributedLockManager


@pytest.mark.asyncio
async def test_distributed_lock_acquisition_and_release():
    lock_mgr = DistributedLockManager()

    lock1 = await lock_mgr.acquire_lock("resource_key", owner_id="owner_a", ttl_seconds=10.0)
    assert lock1 is not None

    # Second owner cannot acquire active lock
    lock2 = await lock_mgr.acquire_lock("resource_key", owner_id="owner_b", ttl_seconds=10.0)
    assert lock2 is None

    # Owner A releases lock
    released = await lock_mgr.release_lock("resource_key", owner_id="owner_a")
    assert released is True

    # Now owner B can acquire lock
    lock3 = await lock_mgr.acquire_lock("resource_key", owner_id="owner_b", ttl_seconds=10.0)
    assert lock3 is not None
