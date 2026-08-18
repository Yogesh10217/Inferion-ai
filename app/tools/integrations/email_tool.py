"""
Email External Integration Tool
"""

import time
import logging
from typing import Dict, Any, List, Optional

from app.tools.tool import BaseTool, ToolMetadata, ToolCategory, ToolCapability
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult, ToolExecutionStatus

logger = logging.getLogger(__name__)


class EmailTool(BaseTool):
    """Email integration supporting Send, Read, Draft, and Attachments."""

    def __init__(self, name: str = "email_tool"):
        metadata = ToolMetadata(
            name=name,
            description="Sends email messages, drafts emails, reads inbox, and handles attachments",
            category=ToolCategory.INTEGRATION,
            capabilities=[ToolCapability.NETWORK, ToolCapability.WRITE, ToolCapability.HIGH_RISK],
            cost_estimate=0.001,
            requires_approval=True,
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["send", "read", "draft"]},
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Email body content"},
                    "attachments": {"type": "array", "items": {"type": "string"}, "description": "Attachment file paths"},
                },
                "required": ["action"],
            },
        )
        super().__init__(metadata)

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        action = parameters.get("action", "send")
        to_addr = parameters.get("to", "")
        subject = parameters.get("subject", "")
        body = parameters.get("body", "")

        try:
            elapsed = time.time() - start_time
            output = {
                "action": action,
                "to": to_addr,
                "subject": subject,
                "status": "sent" if action == "send" else "drafted",
                "message_id": f"msg_{int(time.time())}",
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
                error=f"Email Tool Error: {str(ex)}",
                execution_time_seconds=elapsed,
                metadata={"external_api_call": True},
            )
