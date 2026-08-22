"""
Tests for Digital Worker Model
"""

import pytest
from app.workers.worker import DigitalWorker
from app.workers.worker_templates import WorkerTemplateType


@pytest.mark.asyncio
async def test_worker_execute_goal():
    worker = DigitalWorker(name="Test Dev Worker", template_type=WorkerTemplateType.ENGINEERING)
    res = await worker.execute_goal("Build auth service feature")

    assert res["status"] == "COMPLETED"
    assert worker.assigned_goals_count == 1
