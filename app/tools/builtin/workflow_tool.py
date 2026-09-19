"""
Platform Native Workflow Tool (Phase 5.2 Integration)
"""

import logging
import time
from typing import Any, Dict, Optional

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class WorkflowTool(BaseTool):
    """Integrates directly with Phase 5.2 Workflow Subsystem."""

    def __init__(self, name: str = "workflow_runner", workflow_manager: Optional[Any] = None):
        metadata = ToolMetadata(
            name=name,
            description="Triggers and monitors DAG workflow executions (Phase 5.2)",
            category=ToolCategory.WORKFLOW,
            capabilities=[ToolCapability.EXECUTE],
            cost_estimate=0.001,
            parameters_schema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "Workflow identifier"},
                    "inputs": {"type": "object", "description": "Initial execution inputs"},
                    "action": {"type": "string", "enum": ["run", "status", "cancel"]},
                },
                "required": ["workflow_id"],
            },
        )
        super().__init__(metadata)
        self.workflow_manager = workflow_manager

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        workflow_id = parameters.get("workflow_id", "")
        inputs = parameters.get("inputs") or {}
        action = parameters.get("action", "run")

        try:
            from app.workflows.workflow_manager import WorkflowManager

            wm = self.workflow_manager or WorkflowManager()

            if action == "run":
                exec_state = await wm.execute_workflow(workflow_id, inputs=inputs)
                output = {"status": "completed", "workflow_id": workflow_id, "state": exec_state.to_dict()}
            elif action == "status":
                w_status = wm.get_execution(workflow_id)
                output = {"workflow_id": workflow_id, "status": w_status}
            else:
                output = {"workflow_id": workflow_id, "action": action, "status": "processed"}

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
                error=f"Workflow Tool Error: {str(ex)}",
                execution_time_seconds=elapsed,
            )
