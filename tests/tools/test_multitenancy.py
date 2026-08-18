"""
Tests for Multi-tenant Isolation and Boundary Rules
"""

import pytest
from app.tools.tool import BaseTool, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_registry import ToolRegistry
from app.tools.tool_executor import ToolExecutor
from app.tools.tool_result import ToolResult, ToolExecutionStatus
from app.tools.exceptions import ToolNotFoundException, ToolPermissionDenied


class TenantTestTool(BaseTool):
    def __init__(self, name: str, tenant_id: str):
        meta = ToolMetadata(name=name, description="Tenant tool", tenant_id=tenant_id)
        super().__init__(meta)

    async def execute_async(self, parameters: dict, context: ToolContext) -> ToolResult:
        return ToolResult(execution_id=context.execution_id, tool_name=self.name, status=ToolExecutionStatus.SUCCESS)


@pytest.mark.asyncio
async def test_tenant_registry_isolation():
    registry = ToolRegistry()
    t1 = TenantTestTool("private_tool", "org_alpha")
    t2 = TenantTestTool("private_tool", "org_beta")

    registry.register_tool(t1, tenant_id="org_alpha")
    registry.register_tool(t2, tenant_id="org_beta")

    tool_a = registry.get_tool("private_tool", tenant_id="org_alpha")
    tool_b = registry.get_tool("private_tool", tenant_id="org_beta")

    assert tool_a.metadata.tenant_id == "org_alpha"
    assert tool_b.metadata.tenant_id == "org_beta"


@pytest.mark.asyncio
async def test_tenant_execution_permission_isolation():
    registry = ToolRegistry()
    t1 = TenantTestTool("isolated_tool", "org_alpha")
    registry.register_tool(t1, tenant_id="org_alpha")

    executor = ToolExecutor(registry=registry)
    ctx_beta = ToolContext(tenant_id="org_beta")

    with pytest.raises(ToolNotFoundException):
        await executor.execute_async("isolated_tool", {}, context=ctx_beta)
