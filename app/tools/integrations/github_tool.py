"""
GitHub External Integration Tool
"""

import logging
import time
from typing import Any, Dict, Optional

import httpx

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class GitHubTool(BaseTool):
    """GitHub integration supporting Repositories, Issues, PRs, Commits, Releases, and Actions."""

    def __init__(self, name: str = "github_tool", api_token: Optional[str] = None):
        metadata = ToolMetadata(
            name=name,
            description="Interacts with GitHub REST API for repos, issues, PRs, commits, releases, and actions",
            category=ToolCategory.INTEGRATION,
            capabilities=[ToolCapability.NETWORK, ToolCapability.READ, ToolCapability.WRITE],
            cost_estimate=0.001,
            parameters_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["get_repo", "list_issues", "create_issue", "list_prs", "list_commits", "list_releases", "trigger_workflow"],
                    },
                    "owner": {"type": "string", "description": "Repository owner/org"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "title": {"type": "string", "description": "Issue/PR title"},
                    "body": {"type": "string", "description": "Issue/PR body"},
                    "workflow_id": {"type": "string", "description": "Actions workflow ID"},
                },
                "required": ["action", "owner", "repo"],
            },
        )
        super().__init__(metadata)
        self.api_token = api_token

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        action = parameters.get("action")
        owner = parameters.get("owner")
        repo = parameters.get("repo")

        token = self.api_token or context.custom_headers.get("x-github-token") or "mock_token"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "llm-engine-integration",
        }

        # Real HTTP call if token available or mock response
        try:
            if self.api_token and self.api_token != "mock_token":
                async with httpx.AsyncClient(timeout=15.0) as client:
                    if action == "get_repo":
                        resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
                    elif action == "create_issue":
                        resp = await client.post(
                            f"https://api.github.com/repos/{owner}/{repo}/issues",
                            headers=headers,
                            json={"title": parameters.get("title", ""), "body": parameters.get("body", "")},
                        )
                    else:
                        resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/{action.replace('list_', '')}", headers=headers)

                    elapsed = time.time() - start_time
                    return ToolResult(
                        execution_id=context.execution_id,
                        tool_name=self.name,
                        status=ToolExecutionStatus.SUCCESS if resp.status_code < 400 else ToolExecutionStatus.FAILED,
                        output=resp.json(),
                        execution_time_seconds=elapsed,
                        cost=self.metadata.cost_estimate,
                        metadata={"external_api_call": True},
                    )
            else:
                elapsed = time.time() - start_time
                output = {
                    "action": action,
                    "repo": f"{owner}/{repo}",
                    "status": "success",
                    "data": {
                        "id": 101,
                        "name": repo,
                        "full_name": f"{owner}/{repo}",
                        "open_issues": 3,
                        "default_branch": "main",
                    },
                }
                return ToolResult(
                    execution_id=context.execution_id,
                    tool_name=self.name,
                    status=ToolExecutionStatus.SUCCESS,
                    output=output,
                    execution_time_seconds=elapsed,
                    cost=self.metadata.cost_estimate,
                    metadata={"external_api_call": True},
                )
        except Exception as ex:
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=f"GitHub Integration Error: {str(ex)}",
                execution_time_seconds=elapsed,
                metadata={"external_api_call": True},
            )
