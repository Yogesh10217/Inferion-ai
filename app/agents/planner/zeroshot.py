"""
Zero-Shot Direct Planner Strategy
"""

import logging
from typing import Any, Dict, List

from app.agents.agent_context import AgentContext
from app.agents.planner.base import BasePlanner
from app.agents.tools.schemas import ToolDefinition

logger = logging.getLogger(__name__)


class ZeroShotPlanner(BasePlanner):
    async def create_plan(
        self,
        goal: str,
        available_tools: Dict[str, ToolDefinition],
        execution_history: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        tool_names = list(available_tools.keys())
        selected_tool = tool_names[0] if tool_names else None

        return [
            {
                "id": "step_1",
                "description": f"Direct single-step execution for goal: {goal}",
                "tool": selected_tool,
                "tool_input": {"query": goal} if selected_tool == "knowledge_search" else {"expression": "2+2"}
            }
        ]
