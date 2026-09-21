"""
Planner Unit Tests
"""

import pytest

from app.agents.agent_context import AgentContext
from app.agents.exceptions import PlanningError
from app.agents.planner.factory import PlannerFactory
from app.agents.planner.plan_execute import PlanExecutePlanner
from app.agents.planner.react import ReActPlanner
from app.agents.planner.tree_of_thought import TreeOfThoughtPlanner
from app.agents.planner.zeroshot import ZeroShotPlanner
from app.agents.tools.builtin import BUILTIN_TOOLS


@pytest.mark.asyncio
async def test_planner_factory():
    p_react = PlannerFactory.get_planner("react")
    assert isinstance(p_react, ReActPlanner)

    p_zero = PlannerFactory.get_planner("zeroshot")
    assert isinstance(p_zero, ZeroShotPlanner)

    p_pe = PlannerFactory.get_planner("plan_execute")
    assert isinstance(p_pe, PlanExecutePlanner)

    p_tot = PlannerFactory.get_planner("tree_of_thought")
    assert isinstance(p_tot, TreeOfThoughtPlanner)

    with pytest.raises(PlanningError):
        PlannerFactory.get_planner("unknown_strategy")


@pytest.mark.asyncio
async def test_react_planner_creates_step():
    planner = ReActPlanner()
    ctx = AgentContext()
    available_tools = {k: v["definition"] for k, v in BUILTIN_TOOLS.items()}

    plan = await planner.create_plan(
        goal="Calculate 10 + 20", available_tools=available_tools, execution_history=[], context=ctx
    )
    assert len(plan) == 1
    assert plan[0]["tool"] == "calculator"
    assert "10 + 20" in plan[0]["tool_input"]["expression"]
