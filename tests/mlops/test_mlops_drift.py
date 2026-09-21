"""Unit tests for DriftDetector."""

from app.mlops.deployment import DeploymentManager, DeploymentStatus
from app.mlops.drift import DriftDetector, DriftType
from app.mlops.registry import AIAssetRegistry, AIAssetType


def test_drift_detection_and_degraded_state_trigger():
    registry = AIAssetRegistry()
    asset = registry.register_asset("Drift Bot", AIAssetType.AGENT)
    dep_mgr = DeploymentManager(registry=registry)
    dep = dep_mgr.create_deployment("Drift Dep", asset.asset_id, "1.0.0")

    detector = DriftDetector(deployment_manager=dep_mgr)

    # 100ms baseline -> 200ms current (+100% latency drift)
    res = detector.detect_drift(dep.deployment_id, DriftType.LATENCY_DRIFT, baseline_value=100.0, current_value=200.0)

    assert res is not None
    assert res.severity == "CRITICAL"
    assert res.deviation_percent == 100.0

    updated_dep = dep_mgr.get_deployment(dep.deployment_id)
    assert updated_dep.status == DeploymentStatus.DEGRADED
