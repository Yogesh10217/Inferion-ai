"""
Tests for Workflow Integration with Agent Teams (Phase 5.2)
"""

import pytest
from app.workflows.node import AgentNode, NodeType


@pytest.mark.asyncio
async def test_agent_node_workflow_execution():
    node = AgentNode(node_id="node_team_1", name="Team Execution Node", agent_id="team_engineering")
    context = {
        "organization_id": "org_a",
        "prompt": "Build user auth service",
    }
    output = await node.execute(context)
    assert output["agent_id"] == "team_engineering"
    assert output["status"] == "completed"
