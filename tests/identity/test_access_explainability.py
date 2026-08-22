"""Unit tests for deterministic authorization decision explanations."""

import pytest
from app.identity.explainability import ExplainabilityEngine
from app.identity.access_control import AccessContext, AccessDecision, AccessDecisionType


def test_access_decision_explainability():
    engine = ExplainabilityEngine()

    ctx = AccessContext(identity_id="user_test", role="developer", data_classification="RESTRICTED", authentication_level="STANDARD")
    dec = AccessDecision(decision=AccessDecisionType.REQUIRE_STEP_UP_AUTH, allow=False, required_assurance="HIGH", reason="Step-up required for RESTRICTED data")

    expl = engine.explain_access_decision("read", ctx, dec)

    assert expl.is_deterministic is True
    assert "DENIED" in expl.outcome
    assert expl.required_assurance == "HIGH"
    assert "Identity Role: developer" in expl.contributing_factors
