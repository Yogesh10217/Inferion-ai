"""
Tests for DAG Dependency Graph Engine
"""

import pytest

from app.planning.dependency_graph import DependencyGraph
from app.planning.exceptions import DependencyResolutionError
from app.planning.goals import Task


def test_dag_topological_sort_and_critical_path():
    t1 = Task(task_id="t1", title="Task 1", estimated_duration_seconds=5.0)
    t2 = Task(task_id="t2", title="Task 2", dependencies=["t1"], estimated_duration_seconds=10.0)
    t3 = Task(task_id="t3", title="Task 3", dependencies=["t2"], estimated_duration_seconds=5.0)

    graph = DependencyGraph([t1, t2, t3])
    order = graph.get_execution_order()
    assert order == ["t1", "t2", "t3"]

    crit = graph.calculate_critical_path()
    assert crit == ["t1", "t2", "t3"]


def test_dag_cycle_detection():
    t1 = Task(task_id="t1", title="Task 1", dependencies=["t2"])
    t2 = Task(task_id="t2", title="Task 2", dependencies=["t1"])

    graph = DependencyGraph([t1, t2])
    assert graph.detect_cycle() is True
    with pytest.raises(DependencyResolutionError):
        graph.get_execution_order()
