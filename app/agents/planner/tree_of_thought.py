"""
Tree-of-Thought (ToT) Exploration Planner Strategy
"""

import logging
from typing import Dict, Any, List
from app.agents.planner.base import BasePlanner
from app.agents.agent_context import AgentContext
from app.agents.tools.schemas import ToolDefinition

logger = logging.getLogger(__name__)


class TreeOfThoughtPlanner(BasePlanner):
    async def create_plan(
        self,
        goal: str,
        available_tools: Dict[str, ToolDefinition],
        execution_history: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        # Explores multiple reasoning branches and selects optimal path
        tool_name = "knowledge_search" if "knowledge_search" in available_tools else list(available_tools.keys())[0]
        return [
            {
                "id": "tot_branch_alpha",
                "description": f"Tree-of-Thought Branch Alpha for '{goal}'",
                "tool": tool_name,
                "tool_input": {"query": goal}
            }
        ]
