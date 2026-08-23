"""Unit tests for Feature Flags & Deterministic Experimentation."""

import pytest
from app.application_platform.features import (
    FeatureManager,
    FeatureVariant,
    FeatureState,
)


def test_deterministic_experiment_variant_assignment():
    feat_mgr = FeatureManager()
    
    variants = [
        FeatureVariant(variant_id="A", name="Control", weight_percentage=50.0),
        FeatureVariant(variant_id="B", name="Treatment", weight_percentage=50.0),
    ]

    exp = feat_mgr.create_experiment(
        tenant_id="tenant_x",
        application_id="app_web",
        feature_key="new_checkout_flow",
        variants=variants,
    )

    ctx_user_1 = {"user_id": "user_101"}
    eval1_a = feat_mgr.evaluate_feature("tenant_x", "app_web", "new_checkout_flow", ctx_user_1)
    eval1_b = feat_mgr.evaluate_feature("tenant_x", "app_web", "new_checkout_flow", ctx_user_1)

    # Must be deterministic for same user_id
    assert eval1_a["variant"] == eval1_b["variant"]
    assert eval1_a["reason"] == "EXPERIMENT_DETERMINISTIC_ASSIGNMENT"
