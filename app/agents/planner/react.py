"""
ReAct (Reason + Act) Interleaved Planner Strategy
"""

import logging
from typing import Any, Dict, List

from app.agents.agent_context import AgentContext
from app.agents.planner.base import BasePlanner
from app.agents.tools.schemas import ToolDefinition

logger = logging.getLogger(__name__)


class ReActPlanner(BasePlanner):
    async def create_plan(
        self,
        goal: str,
        available_tools: Dict[str, ToolDefinition],
        execution_history: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        step_num = len(execution_history) + 1
        goal_lower = goal.lower()

        # Decide next action based on available tools and goal keywords
        if "calculator" in available_tools and any(kw in goal_lower for kw in ["calc", "math", "+", "-", "*", "/"]):
            return [{
                "id": f"step_{step_num}",
                "description": f"Reason: Execute math calculation for '{goal}'",
                "tool": "calculator",
                "tool_input": {"expression": goal}
            }]
        elif "knowledge_search" in available_tools and not execution_history:
            return [{
                "id": f"step_{step_num}",
                "description": f"Reason: Search knowledge base for '{goal}'",
                "tool": "knowledge_search",
                "tool_input": {"query": goal}
            }]
        else:
            first_tool = list(available_tools.keys())[0] if available_tools else None
            return [{
                "id": f"step_{step_num}",
                "description": f"Reason: Execute tool step for '{goal}'",
                "tool": first_tool,
                "tool_input": {"query": goal}
            }]
