"""Unit tests for JobScheduler."""

import pytest
import asyncio
from app.jobs.job_queue import JobQueue
from app.jobs.job_scheduler import JobScheduler


@pytest.mark.asyncio
async def test_job_scheduler_interval():
    queue = JobQueue()
    scheduler = JobScheduler(queue=queue)

    scheduler.schedule_interval(name="ping_task", handler_name="ping", interval_seconds=0.1)

    await scheduler.start()
    await asyncio.sleep(0.25)
    await scheduler.stop()

    assert len(queue._jobs) >= 1
