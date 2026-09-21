"""Unit tests for ModelLifecycleManager."""

from app.mlops.model_lifecycle import ModelLifecycleManager, ModelProvider
from app.mlops.registry import AIAssetRegistry


def test_model_registration_and_capability_validation():
    registry = AIAssetRegistry()
    mgr = ModelLifecycleManager(registry=registry)

    res = mgr.register_model(
        name="Claude-3 Opus",
        provider=ModelProvider.ANTHROPIC,
        version_str="3.0",
        capabilities=["chat", "tool_calling", "vision"],
    )

    asset_id = res["asset_id"]
    assert mgr.validate_capabilities(asset_id, ["chat", "tool_calling"]) is True
    assert mgr.validate_capabilities(asset_id, ["audio"]) is False
