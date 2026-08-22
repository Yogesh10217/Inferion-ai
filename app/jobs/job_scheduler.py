"""Distributed Job Scheduler integrating Cron, Delayed Jobs, and Periodic Schedules."""

import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel

from app.jobs.job import Job, JobPriority, JobMetadata
from app.jobs.job_queue import JobQueue

logger = logging.getLogger(__name__)


class ScheduledTask(BaseModel):
    """Definition for recurring or delayed background task."""

    task_id: str
    name: str
    handler_name: str
    payload: Dict[str, Any]
    cron_expression: Optional[str] = None
    interval_seconds: Optional[float] = None
    last_run_at: Optional[datetime] = None
    is_active: bool = True


class JobScheduler:
    """Schedules cron & interval tasks and enqueues jobs into JobQueue."""

    def __init__(self, queue: Optional[JobQueue] = None) -> None:
        self.queue = queue or JobQueue()
        self.tasks: Dict[str, ScheduledTask] = {}
        self.is_running: bool = False
        self._loop_task: Optional[asyncio.Task] = None

    def schedule_interval(
        self,
        name: str,
        handler_name: str,
        interval_seconds: float,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: str = "global",
    ) -> ScheduledTask:
        """Schedule a periodic interval task."""
        task_id = f"task_{name}"
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            handler_name=handler_name,
            payload=payload or {},
            interval_seconds=interval_seconds,
        )
        self.tasks[task_id] = task
        logger.info(f"[SCHEDULER] Registered interval task '{name}' (every {interval_seconds}s)")
        return task

    async def start(self) -> None:
        """Start scheduler evaluation loop."""
        self.is_running = True
        self._loop_task = asyncio.create_task(self._run_loop())
        logger.info("[SCHEDULER] Job scheduler started")

    async def stop(self) -> None:
        """Stop scheduler."""
        self.is_running = False
        if self._loop_task and not self._loop_task.done():
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        logger.info("[SCHEDULER] Job scheduler stopped")

    async def _run_loop(self) -> None:
        while self.is_running:
            now = datetime.now(timezone.utc)
            for task in list(self.tasks.values()):
                if not task.is_active:
                    continue

                should_run = False
                if task.interval_seconds:
                    if not task.last_run_at:
                        should_run = True
                    else:
                        elapsed = (now - task.last_run_at).total_seconds()
                        if elapsed >= task.interval_seconds:
                            should_run = True

                if should_run:
                    task.last_run_at = now
                    job = Job(
                        name=task.name,
                        handler_name=task.handler_name,
                        payload=task.payload,
                        priority=JobPriority.NORMAL,
                        metadata=JobMetadata(idempotency_key=f"{task.task_id}_{now.strftime('%Y%m%d%H%M%S')}"),
                    )
                    self.queue.enqueue(job)
                    logger.info(f"[SCHEDULER] Enqueued recurring job for task '{task.name}'")

            await asyncio.sleep(1.0)
