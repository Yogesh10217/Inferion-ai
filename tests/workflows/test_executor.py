"""
Tests for Core Workflow Executor Engine
"""

import pytest
from app.workflows.executor import WorkflowExecutor
from app.workflows.dag import DAGBuilder
from app.workflows.state import WorkflowStatus


@pytest.mark.asyncio
async def test_sequential_workflow_execution():
    builder = DAGBuilder("seq_wf")
    graph = (
        builder.add_start()
        .add_agent("a1", "Agent 1", agent_id="agent_1")
        .add_tool("t1", "Tool 1", tool_name="tool_1")
        .add_end()
        .connect("START", "a1")
        .connect("a1", "t1")
        .connect("t1", "END")
        .build()
    )

    executor = WorkflowExecutor()
    res = await executor.execute_workflow(
        workflow_id="seq_wf",
        graph=graph,
        initial_inputs={"query": "test query"},
        context={"organization_id": "org_demo", "workspace_id": "ws_demo"},
    )

    assert res["status"] == WorkflowStatus.COMPLETED.value
    assert "START" in res["completed_nodes"]
    assert "a1" in res["completed_nodes"]
    assert "t1" in res["completed_nodes"]
    assert "END" in res["completed_nodes"]


@pytest.mark.asyncio
async def test_workflow_execution_pauses_for_approval():
    builder = DAGBuilder("appr_wf")
    graph = (
        builder.add_start()
        .add_agent("a1", "Agent 1", agent_id="agent_1")
        .add_approval("appr1", "Require Signoff")
        .add_end()
        .connect("START", "a1")
        .connect("a1", "appr1")
        .connect("appr1", "END")
        .build()
    )

    executor = WorkflowExecutor()
    res = await executor.execute_workflow(
        workflow_id="appr_wf",
        graph=graph,
        initial_inputs={"query": "approval query"},
        context={"organization_id": "org_demo"},
    )

    assert res["status"] == WorkflowStatus.WAITING_FOR_APPROVAL.value
    assert "approval_request_id" in res
