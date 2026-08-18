"""
Tests for ToolRegistry Subsystem
"""

import pytest
import threading
from app.tools.tool import BaseTool, ToolMetadata, ToolCategory, ToolCapability
from app.tools.tool_registry import ToolRegistry
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult, ToolExecutionStatus
from app.tools.exceptions import ToolNotFoundException, ToolValidationError


class DummyTestTool(BaseTool):
    def __init__(self, name: str = "dummy_tool", version: str = "1.0.0", tenant_id: str = "global"):
        meta = ToolMetadata(
            name=name,
            description="Dummy tool for testing",
            version=version,
            category=ToolCategory.CUSTOM,
            tenant_id=tenant_id,
        )
        super().__init__(meta)

    async def execute_async(self, parameters: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            execution_id=context.execution_id,
            tool_name=self.name,
            status=ToolExecutionStatus.SUCCESS,
            output={"result": "ok"},
        )


@pytest.mark.asyncio
async def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = DummyTestTool(name="test_tool", version="1.0.0", tenant_id="tenant_a")
    registry.register_tool(tool, tenant_id="tenant_a")

    retrieved = registry.get_tool("test_tool", tenant_id="tenant_a")
    assert retrieved.name == "test_tool"
    assert retrieved.metadata.tenant_id == "tenant_a"


@pytest.mark.asyncio
async def test_tool_not_found():
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundException):
        registry.get_tool("non_existent_tool", tenant_id="tenant_a")


@pytest.mark.asyncio
async def test_multi_tenant_isolation_in_registry():
    registry = ToolRegistry()
    tool_a = DummyTestTool(name="shared_tool", version="1.0.0", tenant_id="tenant_a")
    tool_b = DummyTestTool(name="shared_tool", version="2.0.0", tenant_id="tenant_b")

    registry.register_tool(tool_a, tenant_id="tenant_a")
    registry.register_tool(tool_b, tenant_id="tenant_b")

    got_a = registry.get_tool("shared_tool", tenant_id="tenant_a")
    got_b = registry.get_tool("shared_tool", tenant_id="tenant_b")

    assert got_a.version == "1.0.0"
    assert got_b.version == "2.0.0"


@pytest.mark.asyncio
async def test_list_and_search_tools():
    registry = ToolRegistry()
    t1 = DummyTestTool(name="search_alpha", tenant_id="tenant_a")
    t2 = DummyTestTool(name="search_beta", tenant_id="tenant_a")
    registry.register_tool(t1, tenant_id="tenant_a")
    registry.register_tool(t2, tenant_id="tenant_a")

    listed = registry.list_tools(tenant_id="tenant_a")
    assert len(listed) >= 2

    searched = registry.search_tools("alpha", tenant_id="tenant_a")
    assert len(searched) == 1
    assert searched[0].name == "search_alpha"


@pytest.mark.asyncio
async def test_unregister_tool():
    registry = ToolRegistry()
    tool = DummyTestTool(name="temp_tool", tenant_id="tenant_a")
    registry.register_tool(tool, tenant_id="tenant_a")
    assert registry.tool_exists("temp_tool", tenant_id="tenant_a") is True

    unregistered = registry.unregister_tool("temp_tool", tenant_id="tenant_a")
    assert unregistered is True
    assert registry.tool_exists("temp_tool", tenant_id="tenant_a") is False
