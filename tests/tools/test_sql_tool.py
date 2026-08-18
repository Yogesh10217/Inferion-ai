"""
Tests for SQL Query Execution Tool
"""

import pytest
from app.tools.builtin.sql_tool import SQLTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_sql_read_only_allowed():
    tool = SQLTool(read_only=True)
    ctx = ToolContext()
    res = await tool.execute_async({"query": "SELECT * FROM users WHERE age > 21"}, ctx)

    assert res.status == ToolExecutionStatus.SUCCESS
    assert "columns" in res.output


@pytest.mark.asyncio
async def test_sql_write_blocked():
    tool = SQLTool(read_only=True)
    ctx = ToolContext()
    res = await tool.execute_async({"query": "DROP TABLE users"}, ctx)

    assert res.status == ToolExecutionStatus.FAILED
    assert "Read-only SQL policy enforced" in res.error
