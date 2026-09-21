"""Unit tests for agent delegated authorization boundary enforcement in orchestration."""

import pytest

from app.identity.agent_identity import AgentIdentityManager
from app.identity.exceptions import AgentBoundaryViolationException
from app.orchestration.agent_orchestration import AgentOrchestrationManager, AgentTask


def test_agent_delegated_boundary_in_orchestration():
    ag_id_mgr = AgentIdentityManager()
    del_auth = ag_id_mgr.create_delegated_authorization(
        "user_alice", "agent_1", delegated_scopes=["read"], tenant_id="t_del_orch"
    )

    orch_mgr = AgentOrchestrationManager(agent_identity_manager=ag_id_mgr)

    # Valid task
    t_valid = AgentTask(agent_id="agent_1", action="read_doc", delegation_id=del_auth.delegation_id)
    res = orch_mgr.execute_agent_task(t_valid, requested_scope="read")
    assert res["status"] == "SUCCESS"

    # Invalid scope -> Exception!
    t_invalid = AgentTask(agent_id="agent_1", action="delete_db", delegation_id=del_auth.delegation_id)
    with pytest.raises(AgentBoundaryViolationException):
        orch_mgr.execute_agent_task(t_invalid, requested_scope="admin")
