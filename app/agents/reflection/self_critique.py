"""
Self-Critique Reflection Strategy
"""

import logging
from typing import Dict, Any, List
from app.agents.reflection.base import BaseReflection
from app.agents.agent_context import AgentContext

logger = logging.getLogger(__name__)


class SelfCritiqueReflection(BaseReflection):
    async def reflect(
        self,
        goal: str,
        execution_history: List[Dict[str, Any]],
        context: AgentContext
    ) -> Dict[str, Any]:
        failed_steps = [s for s in execution_history if s.get("status") == "FAILED"]
        if failed_steps:
            return {
                "is_valid": False,
                "critique": f"Failed step detected: {failed_steps[0].get('error')}",
                "retry_recommended": True,
                "revised_plan": [
                    {
                        "id": "retry_step_1",
                        "description": f"Retry step after failure analysis: {failed_steps[0].get('error')}",
                        "tool": failed_steps[0].get("tool"),
                        "tool_input": failed_steps[0].get("tool_input", {})
                    }
                ]
            }
        return {
            "is_valid": True,
            "critique": "Trajectory self-critique passed with clean execution.",
            "retry_recommended": False,
            "revised_plan": None
        }
