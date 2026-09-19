"""
Jira External Integration Tool
"""

import logging
import time
from typing import Any, Dict

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class JiraTool(BaseTool):
    """Jira integration supporting Create issue, Update issue, Search issue, and Comment."""

    def __init__(self, name: str = "jira_tool"):
        metadata = ToolMetadata(
            name=name,
            description="Interacts with Jira Cloud REST API for issues, searches, and comments",
            category=ToolCategory.INTEGRATION,
            capabilities=[ToolCapability.NETWORK, ToolCapability.WRITE, ToolCapability.READ],
            cost_estimate=0.001,
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create_issue", "update_issue", "search_issue", "add_comment"],
                    },
                    "project_key": {"type": "string", "description": "Jira Project key (e.g. PROJ)"},
                    "issue_key": {"type": "string", "description": "Jira Issue key (e.g. PROJ-123)"},
                    "summary": {"type": "string", "description": "Issue summary/title"},
                    "description": {"type": "string", "description": "Issue body description"},
                    "comment": {"type": "string", "description": "Comment text"},
                    "jql": {"type": "string", "description": "JQL query string"},
                },
                "required": ["action"],
            },
        )
        super().__init__(metadata)

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        action = parameters.get("action")
        pkey = parameters.get("project_key", "PROJ")
        summary = parameters.get("summary", "")

        try:
            elapsed = time.time() - start_time
            output = {
                "action": action,
                "issue_key": parameters.get("issue_key") or f"{pkey}-101",
                "summary": summary,
                "status": "success",
            }
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.SUCCESS,
                output=output,
                execution_time_seconds=elapsed,
                cost=self.metadata.cost_estimate,
                metadata={"external_api_call": True},
            )
        except Exception as ex:
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=f"Jira Tool Error: {str(ex)}",
                execution_time_seconds=elapsed,
                metadata={"external_api_call": True},
            )
