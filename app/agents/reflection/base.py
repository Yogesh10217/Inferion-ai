"""
Base Reflection Engine Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.agents.agent_context import AgentContext


class BaseReflection(ABC):
    @abstractmethod
    async def reflect(
        self, goal: str, execution_history: List[Dict[str, Any]], context: AgentContext
    ) -> Dict[str, Any]:
        """
        Reflects on execution trajectory.
        Returns: {
            "is_valid": bool,
            "critique": str,
            "retry_recommended": bool,
            "revised_plan": Optional[List[Dict[str, Any]]]
        }
        """
