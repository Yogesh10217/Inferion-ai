"""
Base Abstract Planner Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.agents.agent_context import AgentContext
from app.agents.tools.schemas import ToolDefinition


class BasePlanner(ABC):
    @abstractmethod
    async def create_plan(
        self,
        goal: str,
        available_tools: Dict[str, ToolDefinition],
        execution_history: List[Dict[str, Any]],
        context: AgentContext,
    ) -> List[Dict[str, Any]]:
        """
        Generates structured execution plan steps.
        Each step dict: {"id": str, "description": str, "tool": str, "tool_input": dict}
        """
