"""
Planner Subsystem Engine
"""

import logging
import time

from app.planning.dependency_graph import DependencyGraph
from app.planning.exceptions import PlanValidationError
from app.planning.execution_plan import ExecutionPlan
from app.planning.goals import Milestone
from app.planning.task_decomposer import TaskDecomposer

logger = logging.getLogger(__name__)


class Planner:
    """Planner creating, optimizing, validating, and estimating execution plans."""

    def create_plan(self, goal_title: str, description: str = "", tenant_id: str = "default_tenant", workspace_id: str = "default_workspace") -> ExecutionPlan:
        tasks, order = TaskDecomposer.decompose_goal(goal_title, description)
        graph = DependencyGraph(tasks)
        crit_path = graph.calculate_critical_path()

        total_cost = sum(t.estimated_cost for t in tasks)
        total_duration = sum(t.estimated_duration_seconds for t in tasks)

        milestone = Milestone(
            title=f"Complete '{goal_title}'",
            description=description,
            tasks=tasks,
        )

        plan = ExecutionPlan(
            goal_id=f"goal_{int(time.time() * 1000)}",
            title=goal_title,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            milestones=[milestone],
            tasks=tasks,
            execution_order=order,
            critical_path=crit_path,
            estimated_duration_seconds=total_duration,
            estimated_cost=total_cost,
            confidence_score=0.92,
            status="draft",
        )
        logger.info(f"[PLANNER] Created plan '{plan.plan_id}' with {len(tasks)} tasks (est. cost: ${total_cost:.4f})")
        return plan

    def validate_plan(self, plan: ExecutionPlan) -> bool:
        if not plan.tasks:
            raise PlanValidationError("Execution plan contains no tasks")
        graph = DependencyGraph(plan.tasks)
        if graph.detect_cycle():
            raise PlanValidationError("Plan task graph contains circular dependencies")
        return True

    def optimize_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        # Re-order and re-index tasks for minimal critical path duration
        graph = DependencyGraph(plan.tasks)
        plan.execution_order = graph.get_execution_order()
        plan.critical_path = graph.calculate_critical_path()
        plan.confidence_score = min(0.99, plan.confidence_score + 0.05)
        return plan

    def estimate_cost(self, plan: ExecutionPlan) -> float:
        return sum(t.estimated_cost for t in plan.tasks)

    def estimate_duration(self, plan: ExecutionPlan) -> float:
        return sum(t.estimated_duration_seconds for t in plan.tasks)
