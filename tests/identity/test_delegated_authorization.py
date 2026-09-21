"""Unit tests for AI Agent delegated permission boundary enforcement."""

import pytest

from app.identity.agent_identity import AgentIdentityManager
from app.identity.exceptions import AgentBoundaryViolationException


def test_agent_permission_boundary_enforcement():
    mgr = AgentIdentityManager()
    del_auth = mgr.create_delegated_authorization(
        "user_bob", "agent_executor", delegated_scopes=["read", "execute"], tenant_id="t_del"
    )

    # 1. Action within delegated scope -> Valid
    assert mgr.validate_agent_action(del_auth.delegation_id, "execute_task", requested_scope="execute") is True

    # 2. Action outside delegated scope -> Exception!
    with pytest.raises(AgentBoundaryViolationException):
        mgr.validate_agent_action(del_auth.delegation_id, "admin_override", requested_scope="admin")

    # 3. Disallowed action -> Exception!
    with pytest.raises(AgentBoundaryViolationException):
        mgr.validate_agent_action(del_auth.delegation_id, "delete_tenant", requested_scope="execute")
