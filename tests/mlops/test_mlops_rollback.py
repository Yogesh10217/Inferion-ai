"""Unit tests for RollbackManager."""

from app.mlops.deployment import DeploymentManager, DeploymentStatus
from app.mlops.registry import AIAssetRegistry, AIAssetType
from app.mlops.rollback import RollbackManager


def test_deployment_rollback_execution():
    registry = AIAssetRegistry()
    asset = registry.register_asset("Rollback Bot", AIAssetType.AGENT)
    registry.create_version(asset.asset_id, "1.1.0", {"temp": 0.5})

    dep_mgr = DeploymentManager(registry=registry)
    dep = dep_mgr.create_deployment("Rollback Dep", asset.asset_id, "1.1.0")

    rb_mgr = RollbackManager(deployment_manager=dep_mgr, registry=registry)
    plan = rb_mgr.create_rollback_plan(
        dep.deployment_id, target_version_number="1.0.0", reason="Performance regression"
    )
    res = rb_mgr.execute_rollback(plan)

    assert res.success is True
    assert res.restored_version_number == "1.0.0"

    updated_dep = dep_mgr.get_deployment(dep.deployment_id)
    assert updated_dep.status == DeploymentStatus.ROLLED_BACK
    assert updated_dep.version_number == "1.0.0"
