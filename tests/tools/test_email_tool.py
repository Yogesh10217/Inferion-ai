"""
Tests for Email Tool
"""

import pytest
from app.tools.integrations.email_tool import EmailTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_email_tool_send():
    tool = EmailTool()
    ctx = ToolContext()
    res = await tool.execute_async({"action": "send", "to": "user@example.com", "subject": "Test", "body": "Hello"}, ctx)

    assert res.status == ToolExecutionStatus.SUCCESS
    assert res.output["to"] == "user@example.com"
    assert res.output["status"] == "sent"
