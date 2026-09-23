"""
Platform Native Agent Tool (Phase 5.1 Integration)
"""

import logging
import time
from typing import Any, Dict, Optional

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class AgentTool(BaseTool):
    """Integrates directly with Phase 5.1 Agent Subsystem."""

    def __init__(self, name: str = "agent_delegate", agent_manager: Optional[Any] = None):
        metadata = ToolMetadata(
            name=name,
            description="Delegates sub-tasks to autonomous Agents (Phase 5.1)",
            category=ToolCategory.AGENT,
            capabilities=[ToolCapability.EXECUTE],
            cost_estimate=0.005,
            parameters_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent ID to invoke"},
                    "task_prompt": {"type": "string", "description": "Prompt or goal for the agent"},
                    "action": {"type": "string", "enum": ["run", "status", "cancel"]},
                },
                "required": ["agent_id", "task_prompt"],
            },
        )
        super().__init__(metadata)
        self.agent_manager = agent_manager

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        agent_id = parameters.get("agent_id", "")
        prompt = parameters.get("task_prompt", "")
        action = parameters.get("action", "run")

        try:
            from app.agents.agent_manager import AgentManager

            am = self.agent_manager or AgentManager()

            if action == "run":
                state = await am.run_agent(agent_id=agent_id, prompt=prompt)
                output = {
                    "status": "completed",
                    "agent_id": agent_id,
                    "state": state.model_dump() if hasattr(state, "model_dump") else str(state),
                }
            else:
                output = {"agent_id": agent_id, "action": action, "status": "processed"}

            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.SUCCESS,
                output=output,
                execution_time_seconds=elapsed,
                cost=self.metadata.cost_estimate,
            )
        except Exception as ex:
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=f"Agent Tool Error: {str(ex)}",
                execution_time_seconds=elapsed,
            )
