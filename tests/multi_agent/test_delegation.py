"""
Tests for Task Delegation Subsystem
"""

from app.multi_agent.agent_delegation import TaskDelegator
from app.multi_agent.agent_team import AgentTeam, TeamType


def test_task_delegation():
    team = AgentTeam.create_preset_team(TeamType.ENGINEERING, "Dev Team")
    delegator = TaskDelegator(team)

    assigned_member = delegator.delegate_task("Implement REST endpoint", delegator_id="manager_id")
    assert assigned_member is not None
    assert assigned_member.profile.agent_id != "manager_id"
    assert len(delegator.delegation_history) == 1
