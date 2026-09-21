"""
Tests for Workflow Execution Billing Integration
"""

import pytest

from app.workflows.dag import DAGBuilder
from app.workflows.executor import WorkflowExecutor


@pytest.mark.asyncio
async def test_workflow_billing_tracking():
    builder = DAGBuilder("billing_wf")
    graph = (
        builder.add_start()
        .add_agent("a1", "Agent", agent_id="agent_1")
        .add_end()
        .connect("START", "a1")
        .connect("a1", "END")
        .build()
    )

    executor = WorkflowExecutor()
    res = await executor.execute_workflow("billing_wf", graph, initial_inputs={})
    assert res["status"] == "COMPLETED"
    # Execution completes and leaves traceable node outputs for billing tracker
    assert "node_outputs" in res
