"""
Simple Reflection Strategy
"""

import logging
from typing import Dict, Any, List
from app.agents.reflection.base import BaseReflection
from app.agents.agent_context import AgentContext

logger = logging.getLogger(__name__)


class SimpleReflection(BaseReflection):
    async def reflect(
        self,
        goal: str,
        execution_history: List[Dict[str, Any]],
        context: AgentContext
    ) -> Dict[str, Any]:
        has_errors = any(step.get("status") == "FAILED" for step in execution_history)
        return {
            "is_valid": not has_errors,
            "critique": "Execution failed due to step errors" if has_errors else "All steps succeeded",
            "retry_recommended": has_errors,
            "revised_plan": None
        }
