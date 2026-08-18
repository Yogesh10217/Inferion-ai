"""
Tests for Sandboxed Python Tool
"""

import pytest
from app.tools.builtin.python_tool import PythonTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_python_tool_clean_execution():
    tool = PythonTool()
    ctx = ToolContext()
    code = "x = 10\ny = 20\nprint(x + y)"
    res = await tool.execute_async({"code": code}, ctx)

    assert res.status == ToolExecutionStatus.SUCCESS
    assert "30" in res.output["stdout"]


@pytest.mark.asyncio
async def test_python_tool_forbidden_import_blocked():
    tool = PythonTool()
    ctx = ToolContext()
    code = "import os\nos.system('whoami')"
    res = await tool.execute_async({"code": code}, ctx)

    assert res.status == ToolExecutionStatus.FAILED
    assert "Forbidden import 'os'" in res.error
