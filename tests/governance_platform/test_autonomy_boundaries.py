"""Unit tests for constrained autonomous agent boundary enforcement."""

from app.governance_platform.human_oversight import AutonomyLevel, HumanOversightEngine


def test_autonomy_boundary_enforcement():
    engine = HumanOversightEngine()
    pol = engine.create_policy(
        "Agent Alpha Policy",
        "agent_alpha",
        autonomy_level=AutonomyLevel.CONSTRAINED_AUTONOMOUS,
        restricted_data_access_allowed=False,
        config_modification_allowed=False,
        tenant_id="t_bound",
    )

    # 1. Action within boundaries -> Allowed
    res_valid = engine.evaluate_action_autonomy(pol.policy_id, "search_public_docs", is_restricted_data=False)
    assert res_valid["allowed"] is True

    # 2. Privileged action (restricted data access) -> Approval required!
    res_priv = engine.evaluate_action_autonomy(pol.policy_id, "query_customer_ssn", is_restricted_data=True)
    assert res_priv["allowed"] is False
    assert res_priv["requires_approval"] is True
    assert res_priv["approval_request_id"] is not None
