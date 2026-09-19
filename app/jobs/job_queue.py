"""Distributed Job Queue with Priority, Idempotency & Dead-Letter Queuing."""

import heapq
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.jobs.job import Job, JobStatus

logger = logging.getLogger(__name__)


class JobQueue:
    """Production job queue with priority ordering, deduplication, and dead-letter isolation."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}  # job_id -> Job
        self._idempotency_map: Dict[str, str] = {}  # idempotency_key -> job_id
        self._queue: List[tuple] = []  # Heap tuple: (-priority, created_at, job_id)
        self._dead_letter_queue: List[Job] = []  # Dead letter store

    def enqueue(self, job: Job) -> Job:
        """Enqueue a new job with idempotency deduplication."""
        idem_key = job.metadata.idempotency_key
        if idem_key and idem_key in self._idempotency_map:
            existing_id = self._idempotency_map[idem_key]
            logger.info(f"[JOB QUEUE] Idempotency key '{idem_key}' matched existing job '{existing_id}'")
            return self._jobs[existing_id]

        job.status = JobStatus.QUEUED
        self._jobs[job.job_id] = job
        if idem_key:
            self._idempotency_map[idem_key] = job.job_id

        now = datetime.now(timezone.utc)
        if not job.scheduled_at or job.scheduled_at <= now:
            heapq.heappush(self._queue, (-int(job.priority), job.created_at.timestamp(), job.job_id))
            logger.info(f"[JOB QUEUE] Enqueued job '{job.job_id}' (priority={job.priority.name})")
        else:
            logger.info(f"[JOB QUEUE] Scheduled delayed job '{job.job_id}' for {job.scheduled_at.isoformat()}")

        return job

    def schedule(self, job: Job, delay_seconds: float) -> Job:
        """Schedule job for future delayed execution."""
        job.scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        return self.enqueue(job)

    def dequeue(self, worker_id: str, lease_seconds: float = 60.0) -> Optional[Job]:
        """Dequeue highest priority ready job for a worker, establishing lease lock."""
        now = datetime.now(timezone.utc)

        # First move any delayed jobs that are now ready into the priority queue
        for job in list(self._jobs.values()):
            if job.status == JobStatus.QUEUED and job.scheduled_at and job.scheduled_at <= now:
                if not any(j_id == job.job_id for _, _, j_id in self._queue):
                    heapq.heappush(self._queue, (-int(job.priority), job.created_at.timestamp(), job.job_id))

        while self._queue:
            _, _, job_id = heapq.heappop(self._queue)
            job = self._jobs.get(job_id)

            if not job or job.status != JobStatus.QUEUED:
                continue

            # Establish lease
            job.status = JobStatus.RUNNING
            job.started_at = now
            job.lease_owner = worker_id
            job.lease_expires_at = now + timedelta(seconds=lease_seconds)
            job.attempts_made += 1
            logger.info(f"[JOB QUEUE] Dequeued job '{job.job_id}' by worker '{worker_id}'")
            return job

        return None

    def complete(self, job_id: str, result: Optional[Dict[str, Any]] = None) -> Job:
        """Mark job as successfully completed."""
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found")

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.result = result or {}
        job.lease_owner = None
        job.lease_expires_at = None
        logger.info(f"[JOB QUEUE] Job '{job_id}' COMPLETED")
        return job

    def fail(self, job_id: str, error_message: str) -> Job:
        """Handle job failure, scheduling retry or routing to dead-letter queue."""
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found")

        job.error_message = error_message
        job.lease_owner = None
        job.lease_expires_at = None

        if job.attempts_made >= job.max_attempts:
            job.status = JobStatus.DEAD_LETTER
            job.completed_at = datetime.now(timezone.utc)
            self._dead_letter_queue.append(job)
            logger.error(
                f"[JOB QUEUE] Job '{job_id}' max attempts reached ({job.attempts_made}/{job.max_attempts}). Moved to DEAD_LETTER queue"
            )
        else:
            job.status = JobStatus.RETRYING
            backoff_sec = 2.0**job.attempts_made
            job.scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_sec)
            job.status = JobStatus.QUEUED
            logger.warning(
                f"[JOB QUEUE] Job '{job_id}' failed (attempt {job.attempts_made}/{job.max_attempts}). Retrying in {backoff_sec}s..."
            )

        return job

    def retry(self, job_id: str) -> Job:
        """Manually retry a failed or dead-letter job."""
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found")

        job.attempts_made = 0
        job.status = JobStatus.QUEUED
        job.scheduled_at = None
        heapq.heappush(self._queue, (-int(job.priority), job.created_at.timestamp(), job.job_id))
        logger.info(f"[JOB QUEUE] Manually re-queued job '{job_id}'")
        return job

    def cancel(self, job_id: str) -> Job:
        """Cancel a queued or pending job."""
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"Job '{job_id}' not found")

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now(timezone.utc)
        logger.info(f"[JOB QUEUE] Cancelled job '{job_id}'")
        return job

    def get_status(self, job_id: str) -> Optional[Job]:
        """Get job entity by ID."""
        return self._jobs.get(job_id)

    def list_dead_letters(self) -> List[Job]:
        """List dead-letter jobs."""
        return list(self._dead_letter_queue)
