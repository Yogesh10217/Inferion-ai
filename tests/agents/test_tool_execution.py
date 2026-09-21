"""
Tool Execution Unit Tests
"""

import pytest

from app.agents.agent_context import AgentContext
from app.agents.exceptions import ToolNotFoundError, ToolPermissionDeniedError
from app.agents.tools.executor import ToolExecutor


@pytest.mark.asyncio
async def test_builtin_calculator_execution():
    executor = ToolExecutor()
    ctx = AgentContext()

    res = await executor.execute_tool("calculator", {"expression": "15 * 3"}, context=ctx)
    assert res["status"] == "SUCCESS"
    assert res["result"]["result"] == 45


@pytest.mark.asyncio
async def test_tool_permission_denial():
    executor = ToolExecutor()
    # User with Viewer role without admin scope trying to run shell command
    ctx = AgentContext(user_roles=["viewer"])

    with pytest.raises(ToolPermissionDeniedError):
        await executor.execute_tool("shell_executor", {"command": "echo test"}, context=ctx)


@pytest.mark.asyncio
async def test_tool_not_found():
    executor = ToolExecutor()
    ctx = AgentContext()

    with pytest.raises(ToolNotFoundError):
        await executor.execute_tool("non_existent_tool", {}, context=ctx)
