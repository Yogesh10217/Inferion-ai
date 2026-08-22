"""Unit tests for JobQueue."""

import pytest
from app.jobs.job import Job, JobStatus, JobPriority
from app.jobs.job_queue import JobQueue


def test_job_queue_priority_and_dead_letter():
    queue = JobQueue()

    low_job = Job(name="low", handler_name="h", priority=JobPriority.LOW)
    high_job = Job(name="high", handler_name="h", priority=JobPriority.HIGH, max_attempts=1)

    queue.enqueue(low_job)
    queue.enqueue(high_job)

    # High priority job is dequeued first
    dequeued = queue.dequeue(worker_id="w1")
    assert dequeued.job_id == high_job.job_id

    # Fail high job (max_attempts=1) -> moved directly to dead letter
    failed_final = queue.fail(high_job.job_id, "error 1")

    assert failed_final.status == JobStatus.DEAD_LETTER
    assert len(queue.list_dead_letters()) == 1
