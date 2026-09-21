"""
Tests for Restricted Shell Tool
"""

import sys

import pytest

from app.tools.builtin.shell_tool import ShellTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_shell_allowed_command():
    tool = ShellTool()
    ctx = ToolContext()
    cmd = "whoami" if sys.platform == "win32" else "whoami"
    res = await tool.execute_async({"command": cmd}, ctx)

    assert res.status == ToolExecutionStatus.SUCCESS
    assert res.output["stdout"].strip() != ""


@pytest.mark.asyncio
async def test_shell_disallowed_command():
    tool = ShellTool()
    ctx = ToolContext()
    res = await tool.execute_async({"command": "rm", "args": ["-rf", "/"]}, ctx)

    assert res.status == ToolExecutionStatus.FAILED
    assert "is not in the allowed command list" in res.error
