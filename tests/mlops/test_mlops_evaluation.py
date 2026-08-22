"""Unit tests for MLOpsEvaluationEngine."""

import pytest
from app.mlops.evaluation import MLOpsEvaluationEngine, EvaluationCase


def test_evaluation_dataset_and_suite_execution():
    engine = MLOpsEvaluationEngine()

    ds = engine.create_dataset(
        name="Support Benchmark",
        cases=[EvaluationCase(input_prompt="Reset password", expected_output="Click account settings")],
    )

    res = engine.run_evaluation(
        asset_id="asset_supp_agent",
        version_number="1.0.0",
        dataset_id=ds.dataset_id,
        min_quality_score=90.0,
    )

    assert res.passed is True
    assert res.overall_score >= 90.0
    assert len(res.detected_regressions) == 0
