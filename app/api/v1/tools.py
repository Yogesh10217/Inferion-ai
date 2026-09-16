"""
FastAPI Router for Enterprise Tool Calling & MCP Platform (/v1/tools)
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.tools.builtin.agent_tool import AgentTool
from app.tools.builtin.http_tool import HTTPTool
from app.tools.builtin.knowledge_tool import KnowledgeTool
from app.tools.builtin.memory_tool import MemoryTool
from app.tools.builtin.python_tool import PythonTool
from app.tools.builtin.shell_tool import ShellTool
from app.tools.builtin.sql_tool import SQLTool
from app.tools.builtin.workflow_tool import WorkflowTool
from app.tools.exceptions import (
    ToolNotFoundException,
    ToolPermissionDenied,
    ToolValidationError,
)
from app.tools.integrations.confluence_tool import ConfluenceTool
from app.tools.integrations.email_tool import EmailTool
from app.tools.integrations.github_tool import GitHubTool
from app.tools.integrations.jira_tool import JiraTool
from app.tools.integrations.notion_tool import NotionTool
from app.tools.integrations.slack_tool import SlackTool
from app.tools.tool import ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_factory import ToolFactory
from app.tools.tool_manager import ToolManager

router = APIRouter(prefix="/v1/tools", tags=["tools"])

# Global ToolManager instance
_global_tool_manager = ToolManager()

# Pre-register builtins


def _init_builtins():
    for t in [
        PythonTool(), HTTPTool(), SQLTool(), ShellTool(),
        KnowledgeTool(), MemoryTool(), WorkflowTool(), AgentTool(),
        GitHubTool(), SlackTool(), EmailTool(), JiraTool(), NotionTool(), ConfluenceTool()
    ]:
        _global_tool_manager.register_tool(t, tenant_id="global")


_init_builtins()


def get_tool_manager() -> ToolManager:
    return _global_tool_manager


class ToolRegisterSchema(BaseModel):
    name: str
    description: str
    category: str = "custom"
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    cost_estimate: float = 0.0
    requires_approval: bool = False
    tenant_id: str = "global"


class ToolExecutionSchema(BaseModel):
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_tool(
    data: ToolRegisterSchema,
    manager: ToolManager = Depends(get_tool_manager),
):
    """Register a new tool dynamically."""
    meta = ToolMetadata(
        name=data.name,
        description=data.description,
        category=ToolCategory(data.category) if data.category in [c.value for c in ToolCategory] else ToolCategory.CUSTOM,
        parameters_schema=data.parameters_schema,
        cost_estimate=data.cost_estimate,
        requires_approval=data.requires_approval,
        tenant_id=data.tenant_id,
    )

    def dummy_handler(**kwargs):
        return {"status": "success", "input": kwargs}

    tool = ToolFactory.from_function(dummy_handler, name=data.name, description=data.description)
    tool.metadata = meta
    manager.register_tool(tool, tenant_id=data.tenant_id)
    return {"status": "registered", "tool": meta.model_dump()}


@router.get("")
async def list_tools(
    category: Optional[str] = None,
    tenant_id: str = "global",
    manager: ToolManager = Depends(get_tool_manager),
):
    """List all registered tools."""
    tools = manager.registry.list_tools(tenant_id=tenant_id, category=category)
    return {"tools": [t.model_dump() for t in tools]}


@router.get("/{id}")
async def get_tool(
    id: str,
    tenant_id: str = "global",
    manager: ToolManager = Depends(get_tool_manager),
):
    """Get tool metadata by ID/name."""
    try:
        tool = manager.get_tool(id, tenant_id=tenant_id)
        return {"tool": tool.metadata.model_dump()}
    except ToolNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool '{id}' not found")


@router.delete("/{id}")
async def delete_tool(
    id: str,
    tenant_id: str = "global",
    manager: ToolManager = Depends(get_tool_manager),
):
    """Unregister a tool by ID/name."""
    success = manager.unregister_tool(id, tenant_id=tenant_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool '{id}' not found")
    return {"status": "deleted", "id": id}


@router.post("/{id}/execute")
async def execute_tool(
    id: str,
    data: ToolExecutionSchema,
    manager: ToolManager = Depends(get_tool_manager),
):
    """Execute a tool by ID/name."""
    ctx_dict = data.context or {}
    ctx = ToolContext(**ctx_dict) if ctx_dict else ToolContext()

    try:
        res = await manager.executor.execute_async(id, data.parameters, ctx)
        return {"result": res.to_dict()}
    except ToolNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool '{id}' not found")
    except ToolValidationError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except ToolPermissionDenied as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{id}/validate")
async def validate_tool_execution(
    id: str,
    data: ToolExecutionSchema,
    manager: ToolManager = Depends(get_tool_manager),
):
    """Validate tool execution parameters without executing."""
    try:
        tool = manager.get_tool(id)
        from app.tools.tool_validator import ToolValidator
        ToolValidator.validate_parameters(tool, data.parameters)
        return {"valid": True, "tool_name": id}
    except ToolNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool '{id}' not found")
    except ToolValidationError as ve:
        return {"valid": False, "tool_name": id, "error": str(ve)}


@router.get("/{id}/audit")
async def get_tool_audit(
    id: str,
    tenant_id: str = "global",
    manager: ToolManager = Depends(get_tool_manager),
):
    """Retrieve audit logs for a tool."""
    logs = manager.audit_logger.get_audit_logs(tenant_id=tenant_id, tool_name=id)
    return {"tool_name": id, "audit_logs": logs}


@router.get("/{id}/metrics")
async def get_tool_metrics(
    id: str,
    tenant_id: str = "global",
    manager: ToolManager = Depends(get_tool_manager),
):
    """Retrieve metrics for a tool."""
    summary = manager.billing_tracker.get_tenant_billing_summary(tenant_id)
    tool_metrics = summary.get("tool_breakdown", {}).get(id, {"calls": 0, "cost": 0.0, "duration": 0.0})
    return {"tool_name": id, "tenant_id": tenant_id, "metrics": tool_metrics}
