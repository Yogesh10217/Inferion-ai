"""
Plan-and-Execute Decomposition Planner Strategy
"""

import logging
from typing import Any, Dict, List

from app.agents.agent_context import AgentContext
from app.agents.planner.base import BasePlanner
from app.agents.tools.schemas import ToolDefinition

logger = logging.getLogger(__name__)


class PlanExecutePlanner(BasePlanner):
    async def create_plan(
        self,
        goal: str,
        available_tools: Dict[str, ToolDefinition],
        execution_history: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        # Pre-decompose goal into sub-goals
        steps = []
        if "knowledge_search" in available_tools:
            steps.append({
                "id": "step_1",
                "description": f"Gather knowledge context for: {goal}",
                "tool": "knowledge_search",
                "tool_input": {"query": goal}
            })
        if "calculator" in available_tools:
            steps.append({
                "id": "step_2",
                "description": "Perform verification calculation",
                "tool": "calculator",
                "tool_input": {"expression": "1 + 1"}
            })
        if not steps:
            steps.append({
                "id": "step_1",
                "description": f"Execute task: {goal}",
                "tool": None,
                "tool_input": {}
            })
        return steps
