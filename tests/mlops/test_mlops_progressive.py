"""Unit tests for ProgressiveDeliveryManager (Canary, Blue-Green, Shadow)."""

import pytest
from app.mlops.registry import AIAssetRegistry, AIAssetType
from app.mlops.deployment import DeploymentManager
from app.mlops.progressive_delivery import ProgressiveDeliveryManager


def test_canary_deployment_scaling_and_auto_rollback():
    registry = AIAssetRegistry()
    asset = registry.register_asset("Canary Bot", AIAssetType.AGENT)
    dep_mgr = DeploymentManager(registry=registry)
    dep = dep_mgr.create_deployment("Canary Dep", asset.asset_id, "1.0.0")

    prog_mgr = ProgressiveDeliveryManager(deployment_manager=dep_mgr)

    canary = prog_mgr.start_canary(dep.deployment_id, "1.0.0", initial_percent=10.0)
    assert canary.current_traffic_percent == 10.0

    # Step 1: Normal metrics -> increase traffic
    c1 = prog_mgr.increase_canary_traffic(canary.canary_id, error_rate=0.01, latency_ms=100.0)
    assert c1.current_traffic_percent == 30.0

    # Step 2: High error rate -> automatic rollback!
    c2 = prog_mgr.increase_canary_traffic(canary.canary_id, error_rate=0.10, latency_ms=100.0)
    assert c2.status == "ROLLED_BACK"
