"""
Tests for ToolExecutor Subsystem
"""

import pytest
import asyncio
from app.tools.tool import BaseTool, ToolMetadata, ToolCategory, RetryPolicy
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult, ToolExecutionStatus
from app.tools.tool_registry import ToolRegistry
from app.tools.tool_executor import ToolExecutor


class SlowTestTool(BaseTool):
    def __init__(self):
        meta = ToolMetadata(
            name="slow_tool",
            description="Slow tool for testing timeouts",
            timeout=0.1,
            retry_policy=RetryPolicy(max_retries=0),
        )
        super().__init__(meta)

    async def execute_async(self, parameters: dict, context: ToolContext) -> ToolResult:
        await asyncio.sleep(0.5)
        return ToolResult(execution_id=context.execution_id, tool_name=self.name, status=ToolExecutionStatus.SUCCESS)


class FastSuccessTool(BaseTool):
    def __init__(self):
        meta = ToolMetadata(
            name="fast_tool",
            description="Fast success tool",
            cost_estimate=0.005,
        )
        super().__init__(meta)

    async def execute_async(self, parameters: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            execution_id=context.execution_id,
            tool_name=self.name,
            status=ToolExecutionStatus.SUCCESS,
            output={"echo": parameters.get("val")},
            cost=self.metadata.cost_estimate,
        )


@pytest.mark.asyncio
async def test_successful_execution():
    registry = ToolRegistry()
    tool = FastSuccessTool()
    registry.register_tool(tool, tenant_id="tenant_x")

    executor = ToolExecutor(registry=registry)
    ctx = ToolContext(tenant_id="tenant_x")
    res = await executor.execute_async("fast_tool", {"val": "hello"}, context=ctx)

    assert res.is_success() is True
    assert res.output["echo"] == "hello"
    assert res.cost == 0.005


@pytest.mark.asyncio
async def test_execution_timeout():
    registry = ToolRegistry()
    tool = SlowTestTool()
    registry.register_tool(tool, tenant_id="tenant_x")

    executor = ToolExecutor(registry=registry)
    ctx = ToolContext(tenant_id="tenant_x")
    res = await executor.execute_async("slow_tool", {}, context=ctx)

    assert res.status == ToolExecutionStatus.TIMEOUT
    assert "timed out" in res.error


@pytest.mark.asyncio
async def test_batch_execution():
    registry = ToolRegistry()
    tool = FastSuccessTool()
    registry.register_tool(tool, tenant_id="tenant_x")

    executor = ToolExecutor(registry=registry)
    ctx = ToolContext(tenant_id="tenant_x")
    reqs = [
        {"tool_name": "fast_tool", "parameters": {"val": 1}, "tenant_id": "tenant_x"},
        {"tool_name": "fast_tool", "parameters": {"val": 2}, "tenant_id": "tenant_x"},
    ]
    results = await executor.execute_batch(reqs, context=ctx)
    assert len(results) == 2
    assert results[0].output["echo"] == 1
    assert results[1].output["echo"] == 2
