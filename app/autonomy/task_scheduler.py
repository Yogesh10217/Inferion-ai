"""
Task Scheduler with Priority Queues & Cron Support
"""

import time
import heapq
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ScheduledTask(BaseModel):
    task_id: str
    priority: int = 1  # 1 (high) to 5 (low)
    scheduled_time: float
    goal_prompt: str
    tenant_id: str = "default_tenant"
    cron_expr: Optional[str] = None
    is_cancelled: bool = False

    def __lt__(self, other: "ScheduledTask"):
        if self.priority == other.priority:
            return self.scheduled_time < other.scheduled_time
        return self.priority < other.priority


class TaskScheduler:
    """Priority-queue based task scheduler supporting cron & budget awareness."""

    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._queue: List[ScheduledTask] = []

    def schedule_task(
        self,
        task_id: str,
        goal_prompt: str,
        delay_seconds: float = 0.0,
        priority: int = 1,
        tenant_id: str = "default_tenant",
        cron_expr: Optional[str] = None,
    ) -> ScheduledTask:
        sched_time = time.time() + delay_seconds
        task = ScheduledTask(
            task_id=task_id,
            priority=priority,
            scheduled_time=sched_time,
            goal_prompt=goal_prompt,
            tenant_id=tenant_id,
            cron_expr=cron_expr,
        )
        self._tasks[task_id] = task
        heapq.heappush(self._queue, task)
        logger.info(f"[SCHEDULER] Scheduled task '{task_id}' (priority={priority}, in {delay_seconds:.1f}s)")
        return task

    def cancel_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            self._tasks[task_id].is_cancelled = True
            logger.info(f"[SCHEDULER] Cancelled task '{task_id}'")
            return True
        return False

    def execute_due_tasks(self) -> List[ScheduledTask]:
        now = time.time()
        due = []
        while self._queue and self._queue[0].scheduled_time <= now:
            t = heapq.heappop(self._queue)
            if not t.is_cancelled:
                due.append(t)
        return due
