"""
Tests for HTTP Request Tool
"""

import pytest
from app.tools.builtin.http_tool import HTTPTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_http_tool_get():
    tool = HTTPTool()
    ctx = ToolContext()
    res = await tool.execute_async({"method": "GET", "url": "https://httpbin.org/get"}, ctx)

    assert res.status in (ToolExecutionStatus.SUCCESS, ToolExecutionStatus.FAILED)
    if res.is_success():
        assert res.output["status_code"] == 200
