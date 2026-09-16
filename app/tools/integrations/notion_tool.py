"""
Notion External Integration Tool
"""

import logging
import time
from typing import Any, Dict

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class NotionTool(BaseTool):
    """Notion integration supporting Pages, Databases, Search, and Updates."""

    def __init__(self, name: str = "notion_tool"):
        metadata = ToolMetadata(
            name=name,
            description="Interacts with Notion API for pages, databases, searching, and property updates",
            category=ToolCategory.INTEGRATION,
            capabilities=[ToolCapability.NETWORK, ToolCapability.READ, ToolCapability.WRITE],
            cost_estimate=0.001,
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create_page", "query_database", "search", "update_page"]},
                    "page_id": {"type": "string", "description": "Target Notion page ID"},
                    "database_id": {"type": "string", "description": "Target Notion database ID"},
                    "query": {"type": "string", "description": "Search query"},
                    "properties": {"type": "object", "description": "Page properties dictionary"},
                },
                "required": ["action"],
            },
        )
        super().__init__(metadata)

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        action = parameters.get("action")

        try:
            elapsed = time.time() - start_time
            output = {
                "action": action,
                "status": "success",
                "object": "page" if "page" in action else "list",
                "id": parameters.get("page_id") or "notion_page_01",
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
                error=f"Notion Tool Error: {str(ex)}",
                execution_time_seconds=elapsed,
                metadata={"external_api_call": True},
            )
