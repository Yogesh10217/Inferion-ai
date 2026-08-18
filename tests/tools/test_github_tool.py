"""
Tests for GitHub Tool
"""

import pytest
from app.tools.integrations.github_tool import GitHubTool
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus


@pytest.mark.asyncio
async def test_github_tool_get_repo():
    tool = GitHubTool()
    ctx = ToolContext()
    res = await tool.execute_async({"action": "get_repo", "owner": "octocat", "repo": "Hello-World"}, ctx)

    assert res.status == ToolExecutionStatus.SUCCESS
    assert res.output["repo"] == "octocat/Hello-World"
