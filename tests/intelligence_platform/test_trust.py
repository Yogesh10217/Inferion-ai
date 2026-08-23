"""Unit tests for Intelligence Trust Engine & Trust x Risk Decision Matrix."""

import pytest
from app.intelligence_platform.context import ContextBuilder
from app.intelligence_platform.trust import IntelligenceTrustEngine
from app.intelligence_platform.governance import IntelligencePolicyDecision
from app.governance_platform.risk import RiskLevel


def test_trust_score_and_matrix_evaluation():
    ctx = ContextBuilder().assemble_context("t1", primary_resource_id="svc_1")
    trust_engine = IntelligenceTrustEngine()

    trust_score = trust_engine.evaluate_trust(ctx)
    assert trust_score.overall_score > 0.0

    # High Trust + Low Risk -> Autonomous allowed
    can_exec, msg = trust_engine.evaluate_trust_risk_matrix(trust_score.overall_score, RiskLevel.LOW, IntelligencePolicyDecision.ALLOW)
    assert can_exec is True

    # High Trust + High Risk -> Approval required
    can_exec_high, msg_high = trust_engine.evaluate_trust_risk_matrix(trust_score.overall_score, RiskLevel.HIGH, IntelligencePolicyDecision.REQUIRE_APPROVAL)
    assert can_exec_high is False
    assert "requires explicit human approval" in msg_high
