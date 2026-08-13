"""
Tests for Parallel Path Concurrency Execution Engine
"""

import pytest
from app.workflows.parallel import ParallelExecutor
from app.workflows.node import AgentNode, ToolNode, NodeStatus


@pytest.mark.asyncio
async def test_parallel_path_concurrency():
    node1 = AgentNode("a1", "Agent A", agent_id="agent_a")
    node2 = ToolNode("t1", "Tool B", tool_name="tool_b")

    async def mock_exec(node, ctx):
        return await node.execute(ctx)

    context = {"organization_id": "org_demo"}
    results = await ParallelExecutor.execute_parallel([node1, node2], context, mock_exec)

    assert "a1" in results
    assert "t1" in results
    assert node1.status == NodeStatus.COMPLETED
    assert node2.status == NodeStatus.COMPLETED
