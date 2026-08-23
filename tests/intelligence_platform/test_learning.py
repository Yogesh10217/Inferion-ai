"""Unit tests for Continuous Learning & Poisoning Resistance."""

import pytest
from app.intelligence_platform.outcomes import OutcomeEvaluator
from app.intelligence_platform.learning import ContinuousLearningManager
from app.intelligence_platform.exceptions import IntelligenceException


def test_continuous_learning_and_feedback_poisoning_protection():
    evaluator = OutcomeEvaluator()
    meas = evaluator.evaluate_outcome("t1", "rec_1")

    learning_mgr = ContinuousLearningManager()
    insight = learning_mgr.process_outcome_learning("t1", meas, "ROLLBACK_DEPLOYMENT", trust_weight=0.90)

    assert insight.learning_id.startswith("lrn_")

    # Low trust weight triggers feedback poisoning protection
    with pytest.raises(IntelligenceException):
        learning_mgr.process_outcome_learning("t1", meas, "ROLLBACK_DEPLOYMENT", trust_weight=0.20)
