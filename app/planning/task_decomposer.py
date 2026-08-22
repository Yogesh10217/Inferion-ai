"""
Task Decomposer Breakdown Engine
"""

from typing import Dict, Any, List, Tuple
from app.planning.goals import Goal, Objective, Milestone, Task, SubTask, Priority, Status
from app.planning.dependency_graph import DependencyGraph


class TaskDecomposer:
    """Decomposes goals and objectives into structured tasks with dependency mapping."""

    @staticmethod
    def decompose_goal(goal_title: str, goal_description: str = "") -> Tuple[List[Task], List[str]]:
        """Decompose a high-level goal into structured tasks."""
        task1 = Task(
            title=f"Analyze requirements for '{goal_title}'",
            description="Initial analysis and research step",
            priority=Priority.HIGH,
            estimated_duration_seconds=5.0,
            estimated_cost=0.005,
            subtasks=[SubTask(title="Parse prompt specifications"), SubTask(title="Verify inputs")],
        )

        task2 = Task(
            title=f"Build core components for '{goal_title}'",
            description="Main execution phase",
            priority=Priority.HIGH,
            dependencies=[task1.task_id],
            estimated_duration_seconds=15.0,
            estimated_cost=0.02,
            subtasks=[SubTask(title="Implement core logic"), SubTask(title="Connect dependencies")],
        )

        task3 = Task(
            title=f"Verify and test output for '{goal_title}'",
            description="Quality assurance and verification",
            priority=Priority.MEDIUM,
            dependencies=[task2.task_id],
            estimated_duration_seconds=5.0,
            estimated_cost=0.005,
            subtasks=[SubTask(title="Run verification checks")],
        )

        tasks = [task1, task2, task3]
        graph = DependencyGraph(tasks)
        order = graph.get_execution_order()
        return tasks, order
