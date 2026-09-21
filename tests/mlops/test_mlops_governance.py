"""Unit tests for MLOpsGovernanceEngine."""

from app.mlops.evaluation import EvaluationResult
from app.mlops.governance import MLOpsGovernanceEngine


def test_promotion_policy_evaluation():
    engine = MLOpsGovernanceEngine()

    # Good eval -> Approved
    good_eval = EvaluationResult(
        asset_id="a1", version_number="1.0.0", overall_score=95.0, safety_score=98.0, hallucination_rate=0.01
    )
    dec = engine.evaluate_promotion("global", "PRODUCTION", good_eval)

    assert dec.approved is True
    assert dec.requires_approval is True

    # Bad eval -> Rejected
    bad_eval = EvaluationResult(
        asset_id="a1", version_number="1.0.0", overall_score=80.0, safety_score=90.0, hallucination_rate=0.10
    )
    dec_bad = engine.evaluate_promotion("global", "PRODUCTION", bad_eval)

    assert dec_bad.approved is False
    assert len(dec_bad.reasons) > 0
