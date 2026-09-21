"""
Tests for Task Decomposer
"""

from app.planning.task_decomposer import TaskDecomposer


def test_task_decomposer():
    tasks, order = TaskDecomposer.decompose_goal("Implement Payment Gateway")
    assert len(tasks) == 3
    assert len(order) == 3
    assert order[0] == tasks[0].task_id
