"""
Planner Factory
"""

from typing import Dict, Type

from app.agents.exceptions import PlanningError
from app.agents.planner.base import BasePlanner
from app.agents.planner.plan_execute import PlanExecutePlanner
from app.agents.planner.react import ReActPlanner
from app.agents.planner.tree_of_thought import TreeOfThoughtPlanner
from app.agents.planner.zeroshot import ZeroShotPlanner


class PlannerFactory:
    _planners: Dict[str, Type[BasePlanner]] = {
        "zeroshot": ZeroShotPlanner,
        "react": ReActPlanner,
        "plan_execute": PlanExecutePlanner,
        "tree_of_thought": TreeOfThoughtPlanner,
    }

    @classmethod
    def get_planner(cls, strategy: str = "react") -> BasePlanner:
        planner_cls = cls._planners.get(strategy.lower())
        if not planner_cls:
            raise PlanningError(f"Unknown planning strategy '{strategy}'. Available: {list(cls._planners.keys())}")
        return planner_cls()
