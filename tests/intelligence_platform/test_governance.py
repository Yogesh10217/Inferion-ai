"""Unit tests for Intelligence Governance & Risk Evaluation."""

import pytest
from app.intelligence_platform.governance import IntelligenceGovernanceEngine, IntelligencePolicyDecision
from app.governance_platform.risk import RiskLevel


def test_governance_decision_evaluation():
    engine = IntelligenceGovernanceEngine()
    dec, risk_ass = engine.evaluate_decision("t1", "ROLLBACK", "svc_gateway", risk_level_str="HIGH", trust_score=85.0)

    assert dec == IntelligencePolicyDecision.REQUIRE_APPROVAL
    assert risk_ass.risk_level == RiskLevel.HIGH
    assert risk_ass.requires_approval is True
