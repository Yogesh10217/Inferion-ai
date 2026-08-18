"""
Tests for Multi-Agent Tool Integration (Phase 5.4)
"""

import pytest
from app.tools.builtin.python_tool import PythonTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_team_agent_tool_execution():
    tool = PythonTool()
    ctx = ToolContext(tenant_id="org_a", user_id="agent_dev_1", metadata={"approval_status": "approved"})
    res = await tool.execute_async({"code": "res = [x * 2 for x in range(5)]; print(res)"}, ctx)

    assert res.status == ToolExecutionStatus.SUCCESS
    assert "[0, 2, 4, 6, 8]" in res.output["stdout"]
