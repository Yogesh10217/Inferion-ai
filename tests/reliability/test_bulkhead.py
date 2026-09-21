"""Unit tests for Bulkhead."""

import asyncio

import pytest

from app.resilience.bulkhead import Bulkhead, BulkheadFullException, BulkheadPolicy


@pytest.mark.asyncio
async def test_bulkhead_concurrency_limit():
    policy = BulkheadPolicy(max_concurrent_calls=1, max_queued_calls=1)
    bh = Bulkhead("test_bh", policy)

    async def slow_task():
        await asyncio.sleep(0.1)
        return "done"

    task1 = asyncio.create_task(bh.execute_async(slow_task))
    await asyncio.sleep(0.01)

    task2 = asyncio.create_task(bh.execute_async(slow_task))
    await asyncio.sleep(0.01)

    # 3rd task exceeds queue capacity
    with pytest.raises(BulkheadFullException):
        await bh.execute_async(slow_task)

    res1, res2 = await asyncio.gather(task1, task2)
    assert res1 == "done"
    assert res2 == "done"
