"""
Platform Native Memory Tool (Phase 5.3 Integration)
"""

import logging
import time
from typing import Any, Dict, Optional

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class MemoryTool(BaseTool):
    """Integrates directly with Phase 5.3 Memory Subsystem."""

    def __init__(self, name: str = "memory_store", memory_service: Optional[Any] = None):
        metadata = ToolMetadata(
            name=name,
            description="Reads, writes, and retrieves semantic and episodic memory items (Phase 5.3)",
            category=ToolCategory.MEMORY,
            capabilities=[ToolCapability.READ, ToolCapability.WRITE],
            cost_estimate=0.0002,
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["get", "save", "list", "delete"]},
                    "content": {"type": "string", "description": "Memory text content to save"},
                    "memory_id": {"type": "string", "description": "Target memory ID"},
                },
                "required": ["action"],
            },
        )
        super().__init__(metadata)
        self.memory_service = memory_service

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        action = parameters.get("action", "list")
        content = parameters.get("content", "")
        mem_id = parameters.get("memory_id")

        try:
            from app.memory.memory_service import MemoryService
            ms = self.memory_service or MemoryService()

            if action == "save":
                rec = ms.create_memory_entry(
                    content=content,
                    organization_id=context.organization_id,
                    workspace_id=context.workspace_id,
                    user_id=context.user_id,
                )
                output = {"status": "saved", "memory_id": rec.memory_id, "content": rec.content}
            elif action == "get" and mem_id:
                rec = ms.get_memory_entry(mem_id, context.organization_id)
                output = {"status": "found", "memory": rec.to_dict()}
            elif action == "delete" and mem_id:
                deleted = ms.delete_memory_entry(mem_id, context.organization_id)
                output = {"status": "deleted" if deleted else "not_found", "memory_id": mem_id}
            else:
                entries = ms.list_memory_entries(context.organization_id, context.workspace_id)
                output = {"count": len(entries), "entries": [e.to_dict() for e in entries]}

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
                error=f"Memory Tool Error: {str(ex)}",
                execution_time_seconds=elapsed,
            )
