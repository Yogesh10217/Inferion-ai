"""
Tests for Workflow Node Implementations
"""

import pytest
from app.workflows.node import (
    StartNode, EndNode, AgentNode, ToolNode, HumanApprovalNode,
    ConditionNode, ParallelNode, JoinNode, KnowledgeNode, NodeStatus
)
from app.workflows.exceptions import ApprovalRequiredError, RBACPermissionDeniedError, TenantIsolationError


@pytest.mark.asyncio
async def test_start_and_end_node_execution():
    start = StartNode()
    end = EndNode()

    context = {"initial_inputs": {"param1": "value1"}, "variables": {"param1": "value1"}}
    res_start = await start.execute(context)
    assert res_start["param1"] == "value1"
    assert start.status == NodeStatus.COMPLETED

    res_end = await end.execute(context)
    assert res_end["status"] == "success"
    assert end.status == NodeStatus.COMPLETED


@pytest.mark.asyncio
async def test_agent_node_execution():
    agent_node = AgentNode("a1", "Research Agent", agent_id="researcher", role="research")
    context = {"organization_id": "org_test", "prompt": "Investigate AI workflows"}

    result = await agent_node.execute(context)
    assert result["agent_id"] == "researcher"
    assert result["status"] == "completed"
    assert agent_node.status == NodeStatus.COMPLETED


@pytest.mark.asyncio
async def test_agent_node_missing_tenant_context():
    agent_node = AgentNode("a1", "Research Agent", agent_id="researcher")
    with pytest.raises(TenantIsolationError):
        await agent_node.execute({})


@pytest.mark.asyncio
async def test_tool_node_rbac_enforcement():
    tool_node = ToolNode("t1", "Execute SQL", tool_name="db_query", config={"required_role": "db_admin"})
    context = {"roles": ["user"]}

    with pytest.raises(RBACPermissionDeniedError):
        await tool_node.execute(context)

    # Authorized user
    auth_context = {"roles": ["db_admin"]}
    res = await tool_node.execute(auth_context)
    assert res["status"] == "executed"


@pytest.mark.asyncio
async def test_human_approval_node_pauses():
    appr_node = HumanApprovalNode("appr1", "Require Approval")
    context = {"run_id": "run_123"}

    with pytest.raises(ApprovalRequiredError) as exc_info:
        await appr_node.execute(context)
    assert "appr1" in exc_info.value.request_id

    # Resume with approval
    resume_context = {"approval_decision": {"approved": True, "feedback": "Looks good"}}
    res = await appr_node.execute(resume_context)
    assert res["approved"] is True
    assert appr_node.status == NodeStatus.COMPLETED
