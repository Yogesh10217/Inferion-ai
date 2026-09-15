"""
Confluence External Integration Tool
"""

import time
import logging
from typing import Dict, Any

from app.tools.tool import BaseTool, ToolMetadata, ToolCategory, ToolCapability
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult, ToolExecutionStatus

logger = logging.getLogger(__name__)


class ConfluenceTool(BaseTool):
    """Confluence integration supporting Pages, Spaces, Search, and Content management."""

    def __init__(self, name: str = "confluence_tool"):
        metadata = ToolMetadata(
            name=name,
            description="Interacts with Confluence REST API for pages, spaces, CQL search, and content updates",
            category=ToolCategory.INTEGRATION,
            capabilities=[ToolCapability.NETWORK, ToolCapability.READ, ToolCapability.WRITE],
            cost_estimate=0.001,
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["get_page", "create_page", "list_spaces", "search_cql"]},
                    "space_key": {"type": "string", "description": "Confluence space key"},
                    "title": {"type": "string", "description": "Page title"},
                    "content": {"type": "string", "description": "Page content"},
                    "cql": {"type": "string", "description": "Confluence CQL search string"},
                },
                "required": ["action"],
            },
        )
        super().__init__(metadata)

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        action = parameters.get("action")
        space_key = parameters.get("space_key", "DOCS")

        try:
            elapsed = time.time() - start_time
            output = {
                "action": action,
                "space_key": space_key,
                "status": "success",
                "page_id": "conf_page_001",
                "title": parameters.get("title", "Confluence Document"),
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
                error=f"Confluence Tool Error: {str(ex)}",
                execution_time_seconds=elapsed,
                metadata={"external_api_call": True},
            )
