"""Unit tests for HumanTaskManager creation, completion, and escalation."""

import pytest
from app.orchestration.human_tasks import HumanTaskManager, TaskStatus, TaskPriority


def test_human_task_lifecycle():
    mgr = HumanTaskManager()

    task = mgr.create_task("Review Loan Application", assigned_user_id="user_officer", tenant_id="t_ht")
    assert task.status == TaskStatus.ASSIGNED

    # Complete task
    comp_task = mgr.complete_task(task.task_id, outputs={"approved": True})
    assert comp_task.status == TaskStatus.COMPLETED
    assert comp_task.outputs["approved"] is True

    # Escalate new task
    task2 = mgr.create_task("Urgent Fraud Check", tenant_id="t_ht")
    esc_task = mgr.escalate_task(task2.task_id, escalation_reason="Overdue SLA")
    assert esc_task.status == TaskStatus.ESCALATED
    assert esc_task.priority == TaskPriority.CRITICAL
