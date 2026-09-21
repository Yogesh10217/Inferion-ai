"""Unit tests for TrustEngine score calculation across 9 dimensions."""

from app.governance_platform.trust import TrustEngine


def test_trust_score_calculation_and_disclaimer():
    engine = TrustEngine()
    ass = engine.calculate_trust("gpt4_deployment", tenant_id="t_trust")

    assert ass.target_resource_id == "gpt4_deployment"
    assert ass.overall_trust_score > 0.0
    assert "Not a guarantee" in ass.disclaimer
