"""Unit tests for deterministic, evidence-backed decision explanations."""

import pytest
from app.governance_platform.explainability import ExplainabilityEngine
from app.governance_platform.decision import GovernanceDecisionRecord
from app.governance_platform.policy_evaluation import GovernanceDecision


def test_deterministic_decision_explainability():
    engine = ExplainabilityEngine()

    record = GovernanceDecisionRecord(
        action="read_restricted",
        target_resource_id="finance_db",
        decision=GovernanceDecision.BLOCK,
        violations=["Restricted dataset access denied without explicit authorization"],
        risk_score=75.0,
        evidence_ids=["evd_100"],
    )

    expl = engine.explain_decision(record)

    assert expl.is_deterministic is True
    assert "BLOCKED" in expl.outcome
    assert "Restricted dataset access denied" in expl.primary_reason
    assert "evd_100" in expl.evidence_ids
