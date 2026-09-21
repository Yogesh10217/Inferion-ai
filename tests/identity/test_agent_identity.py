"""Unit tests for AI Agent delegated authorization scope creation."""

from app.identity.agent_identity import AgentIdentityManager


def test_agent_delegated_authorization_creation():
    mgr = AgentIdentityManager()

    del_auth = mgr.create_delegated_authorization(
        "user_alice", "agent_researcher", delegated_scopes=["read", "search"], tenant_id="t_ag"
    )
    assert del_auth.user_identity_id == "user_alice"
    assert del_auth.agent_id == "agent_researcher"
    assert "search" in del_auth.delegated_scopes
