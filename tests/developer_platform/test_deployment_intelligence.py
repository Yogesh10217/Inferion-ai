"""Unit tests for DeploymentIntelligenceEngine."""

from app.developer_platform.deployment_intelligence import DeploymentIntelligenceEngine


def test_deployment_telemetry_regression_recommendation():
    engine = DeploymentIntelligenceEngine()

    # Normal error rate -> No recommendation
    assert engine.evaluate_deployment_health("rel_1", error_rate_pct=0.5) is None

    # High error rate (10%) -> Rollback recommendation generated with Approval request ID
    rec = engine.evaluate_deployment_health("rel_2", error_rate_pct=10.0, tenant_id="t_dep_intel")
    assert rec is not None
    assert rec.approval_request_id is not None
