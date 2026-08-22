"""Job Worker & WorkerPool with Heartbeats & Lease Expiration Recovery."""

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime, timezone

from app.jobs.job import Job, JobStatus, JobResult
from app.jobs.job_queue import JobQueue

logger = logging.getLogger(__name__)


class JobWorker:
    """Distributed background worker pulling and processing jobs from queue."""

    def __init__(
        self,
        worker_id: Optional[str] = None,
        queue: Optional[JobQueue] = None,
        handlers: Optional[Dict[str, Callable]] = None,
        poll_interval_seconds: float = 0.5,
    ) -> None:
        self.worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"
        self.queue = queue or JobQueue()
        self.handlers: Dict[str, Callable] = handlers or {}
        self.poll_interval = poll_interval_seconds
        self.is_running: bool = False
        self.last_heartbeat: datetime = datetime.now(timezone.utc)
        self._task: Optional[asyncio.Task] = None

    def register_handler(self, name: str, handler: Callable) -> None:
        """Register job handler function by name."""
        self.handlers[name] = handler

    def send_heartbeat(self) -> None:
        """Send heartbeat timestamp update."""
        self.last_heartbeat = datetime.now(timezone.utc)

    async def start(self) -> None:
        """Start worker polling loop."""
        self.is_running = True
        logger.info(f"[WORKER START] Worker '{self.worker_id}' listening for jobs...")
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self, drain: bool = True) -> None:
        """Gracefully stop worker."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"[WORKER STOP] Worker '{self.worker_id}' stopped")

    async def _run_loop(self) -> None:
        while self.is_running:
            self.send_heartbeat()
            try:
                job = self.queue.dequeue(self.worker_id)
                if job:
                    await self._process_job(job)
                else:
                    await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WORKER ERROR] Worker '{self.worker_id}' loop exception: {e}")
                await asyncio.sleep(self.poll_interval)

    async def _process_job(self, job: Job) -> None:
        handler = self.handlers.get(job.handler_name)
        if not handler:
            err = f"No handler registered for '{job.handler_name}'"
            self.queue.fail(job.job_id, err)
            return

        start_t = time.time()
        try:
            if asyncio.iscoroutinefunction(handler):
                res = await handler(**job.payload)
            else:
                res = handler(**job.payload)

            output = res if isinstance(res, dict) else {"result": res}
            self.queue.complete(job.job_id, result=output)
        except Exception as exc:
            self.queue.fail(job.job_id, str(exc))


class WorkerPool:
    """Pool managing multiple background worker instances."""

    def __init__(self, size: int = 3, queue: Optional[JobQueue] = None) -> None:
        self.size = size
        self.queue = queue or JobQueue()
        self.workers: List[JobWorker] = []

    def register_handler(self, name: str, handler: Callable) -> None:
        for w in self.workers:
            w.register_handler(name, handler)

    async def start(self) -> None:
        self.workers = [
            JobWorker(worker_id=f"pool_worker_{i+1}", queue=self.queue)
            for i in range(self.size)
        ]
        for w in self.workers:
            await w.start()
        logger.info(f"[WORKER POOL] Started {self.size} workers")

    async def stop(self) -> None:
        for w in self.workers:
            await w.stop()
        logger.info("[WORKER POOL] Stopped all workers")

