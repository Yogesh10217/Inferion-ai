"""
Tests for Workflow Integration (Phase 5.2)
"""

import pytest

from app.workflows.node import AgentNode


@pytest.mark.asyncio
async def test_workflow_node_planning():
    node = AgentNode(node_id="n_plan", name="Planner Node", agent_id="planner_agent")
    res = await node.execute({"prompt": "Plan deployment", "organization_id": "org_default"})
    assert res["status"] == "completed"
