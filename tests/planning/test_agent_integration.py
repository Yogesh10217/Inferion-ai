"""
Tests for Agent Integration (Phase 5.1 / Phase 5.5)
"""

import pytest

from app.multi_agent.agent_coordinator import MultiAgentCoordinator
from app.multi_agent.agent_team import AgentTeam, TeamExecutionContext, TeamType


@pytest.mark.asyncio
async def test_agent_team_planning_integration():
    team = AgentTeam.create_preset_team(TeamType.ENGINEERING, "Dev Team Plan")
    coord = MultiAgentCoordinator()
    ctx = TeamExecutionContext(team_id=team.team_id, goal="Execute planned task DAG")

    res = await coord.execute_team_run(team, ctx)
    assert res["status"] == "completed"
