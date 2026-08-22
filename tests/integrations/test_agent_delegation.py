"""Unit tests for AgentIntegrationAdapter and agent boundary validation."""

import pytest
from app.integrations.agent_integration import AgentIntegrationAdapter
from app.identity.exceptions import AgentBoundaryViolationException


def test_agent_integration_delegated_scope_enforcement():
    adapter = AgentIntegrationAdapter()

    # Create delegated authorization with read scope only
    del_auth = adapter.agent_identity_manager.create_delegated_authorization(
        user_identity_id="parent_agent_1",
        agent_id="child_agent_1",
        delegated_scopes=["read"],
        tenant_id="t_ag_del",
    )

    # Allowed read action succeeds
    res_read = adapter.execute_external_action_for_agent(
        agent_id="child_agent_1",
        integration_name="github",
        action="read_repo",
        delegation_id=del_auth.delegation_id,
    )
    assert res_read["status"] == "SUCCESS"

    # Attempting write/delete action beyond scope raises AgentBoundaryViolationException
    with pytest.raises(AgentBoundaryViolationException):
        adapter.execute_external_action_for_agent(
            agent_id="child_agent_1",
            integration_name="github",
            action="delete_repo",
            delegation_id=del_auth.delegation_id,
        )
