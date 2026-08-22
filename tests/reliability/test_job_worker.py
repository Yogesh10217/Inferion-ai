"""Unit tests for JobWorker."""

import pytest
import asyncio
from app.jobs.job import Job
from app.jobs.job_queue import JobQueue
from app.jobs.job_worker import JobWorker


@pytest.mark.asyncio
async def test_job_worker_execution():
    queue = JobQueue()
    worker = JobWorker(worker_id="test_w", queue=queue)

    processed = False

    def handle_sample(message: str):
        nonlocal processed
        processed = True
        return {"result": f"processed {message}"}

    worker.register_handler("sample_handler", handle_sample)

    job = Job(name="test_j", handler_name="sample_handler", payload={"message": "hello"})
    queue.enqueue(job)

    await worker.start()
    await asyncio.sleep(0.2)
    await worker.stop()

    assert processed is True
    status = queue.get_status(job.job_id)
    assert status.status.value == "COMPLETED"
