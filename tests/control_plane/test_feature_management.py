"""Unit tests for FeatureManager & FeatureEvaluator."""

from app.control_plane.feature_evaluation import FeatureEvaluator
from app.control_plane.feature_management import FeatureManager


def test_feature_rollout_and_evaluation():
    mgr = FeatureManager()
    evaluator = FeatureEvaluator(manager=mgr)

    # Create feature
    mgr.create_feature("new_reasoning_engine", default_enabled=False)

    # Evaluates False initially
    assert evaluator.is_feature_enabled("new_reasoning_engine") is False

    # Targeted tenant rollout
    mgr.configure_rollout("new_reasoning_engine", tenant_ids=["tenant_vip"])

    assert evaluator.is_feature_enabled("new_reasoning_engine", tenant_id="tenant_vip") is True
    assert evaluator.is_feature_enabled("new_reasoning_engine", tenant_id="tenant_standard") is False

    # Rollback feature
    mgr.rollback_feature("new_reasoning_engine")
    assert evaluator.is_feature_enabled("new_reasoning_engine", tenant_id="tenant_vip") is False
