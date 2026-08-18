"""
Tests for Slack Tool
"""

import pytest
from app.tools.integrations.slack_tool import SlackTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_slack_tool_post_message():
    tool = SlackTool()
    ctx = ToolContext()
    res = await tool.execute_async({"action": "post_message", "channel": "general", "text": "Hello Slack!"}, ctx)

    assert res.status == ToolExecutionStatus.SUCCESS
    assert res.output["ok"] is True
    assert res.output["text"] == "Hello Slack!"
