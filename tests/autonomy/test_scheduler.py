"""
Tests for Task Scheduler
"""

import time

from app.autonomy.task_scheduler import TaskScheduler


def test_task_scheduler_priority_and_due():
    sched = TaskScheduler()
    sched.schedule_task("t_low", "Low priority goal", delay_seconds=0.0, priority=5)
    sched.schedule_task("t_high", "High priority goal", delay_seconds=0.0, priority=1)

    time.sleep(0.01)
    due = sched.execute_due_tasks()
    assert len(due) == 2
    assert due[0].task_id == "t_high"
