"""Unit tests for IntegrationGovernanceEngine and high-risk action approval gating."""

from app.integrations.governance import IntegrationDecisionType, IntegrationGovernanceEngine


def test_integration_governance_risk_evaluation():
    gov = IntegrationGovernanceEngine()

    # Low risk -> ALLOW
    dec_low = gov.evaluate_external_action("slack", action="post_message", risk_level="LOW")
    assert dec_low.decision == IntegrationDecisionType.ALLOW

    # High risk -> REQUIRE_APPROVAL
    dec_high = gov.evaluate_external_action("github", action="delete_repo", risk_level="HIGH")
    assert dec_high.decision == IntegrationDecisionType.REQUIRE_APPROVAL
    assert dec_high.approval_request_id is not None
