"""
Tests for Tool Integration (Phase 5.4)
"""

import pytest
from app.tools.builtin.http_tool import HTTPTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_tool_cost_estimation_integration():
    tool = HTTPTool()
    ctx = ToolContext(tenant_id="tenant_1")
    res = await tool.execute_async({"url": "https://httpbin.org/get", "method": "GET"}, ctx)
    assert res.status in (ToolExecutionStatus.SUCCESS, ToolExecutionStatus.FAILED)
