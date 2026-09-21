"""Unit tests for GovernanceMonitoringEngine compliance drift scans."""

from app.governance_platform.monitoring import GovernanceMonitoringEngine


def test_governance_monitoring_scan():
    engine = GovernanceMonitoringEngine()
    res = engine.run_monitoring_scan(tenant_id="t_mon", target_resource_id="res_check")

    assert res.target_resource_id == "res_check"
    assert res.check_id is not None
