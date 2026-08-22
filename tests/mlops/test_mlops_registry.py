"""Unit tests for AI Asset Registry and Immutable Production Versioning."""

import pytest
from app.mlops.registry import AIAssetRegistry, AIAssetType, AIAssetStatus
from app.mlops.exceptions import AssetNotFoundException, VersionNotFoundException


def test_asset_registration_versioning_and_immutability():
    registry = AIAssetRegistry()

    asset = registry.register_asset(
        name="GPT-4 Turbo",
        asset_type=AIAssetType.MODEL,
        tenant_id="tenant_mlops",
        description="Core chat model",
        initial_configuration={"model_provider": "OPENAI", "context_window": 128000},
    )

    assert asset.name == "GPT-4 Turbo"
    assert asset.current_version == "1.0.0"

    # Create new version
    ver2 = registry.create_version(
        asset_id=asset.asset_id,
        version_number="1.1.0",
        configuration={"model_provider": "OPENAI", "context_window": 128000, "temperature": 0.2},
        changelog="Lowered temperature",
    )
    assert ver2.version_number == "1.1.0"
    assert ver2.is_immutable is False

    # Promote to production locks version as immutable
    promoted = registry.promote_version(asset.asset_id, "1.1.0", AIAssetStatus.PRODUCTION)
    assert promoted.is_immutable is True
    assert promoted.status == AIAssetStatus.PRODUCTION


def test_asset_not_found():
    registry = AIAssetRegistry()
    with pytest.raises(AssetNotFoundException):
        registry.get_asset("nonexistent_asset")
