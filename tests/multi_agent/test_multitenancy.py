"""
Tests for Multi-Tenant Isolation & Security Governance
"""

import pytest
from app.multi_agent.agent_team import AgentTeam, TeamType, TeamExecutionContext
from app.multi_agent.agent_governance import AgentGovernanceEngine
from app.multi_agent.exceptions import RolePermissionDenied


def test_tenant_isolation_in_governance():
    team = AgentTeam.create_preset_team(TeamType.RESEARCH, "Research Team", tenant_id="tenant_alpha")
    ctx = TeamExecutionContext(team_id=team.team_id, goal="Find paper", tenant_id="tenant_beta")

    with pytest.raises(RolePermissionDenied) as exc:
        AgentGovernanceEngine.validate_team_execution(team, ctx)

    assert "Tenant isolation violation" in str(exc.value)


def test_budget_limit_governance():
    team = AgentTeam.create_preset_team(TeamType.RESEARCH, "Research Team", tenant_id="tenant_alpha")
    team.config.budget_dollars = 1.0
    ctx = TeamExecutionContext(team_id=team.team_id, goal="Find paper", tenant_id="tenant_alpha")

    with pytest.raises(RolePermissionDenied) as exc:
        AgentGovernanceEngine.validate_team_execution(team, ctx, estimated_cost=5.0)

    assert "Budget limit exceeded" in str(exc.value)
