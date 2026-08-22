"""
Tests for Worker Manager
"""

import pytest
from app.workers.worker_manager import WorkerManager


@pytest.mark.asyncio
async def test_worker_manager_crud_and_assign():
    mgr = WorkerManager()
    worker = mgr.create_worker("Research Bot", template_type="research")

    assert worker.worker_id in [w.worker_id for w in mgr.list_workers()]

    res = await mgr.assign_goal(worker.worker_id, "Summarize paper")
    assert res["status"] == "COMPLETED"

    ok = mgr.terminate_worker(worker.worker_id)
    assert ok is True
    assert mgr.get_worker(worker.worker_id).status == "terminated"
