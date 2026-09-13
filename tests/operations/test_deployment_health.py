from app.operations.deployment_health import DeploymentHealthCorrelator
from app.operations.observability_engine import ObservabilityEngine


def test_deployment_health_correlation():
    correlator = DeploymentHealthCorrelator()
    obs = ObservabilityEngine().collect_observations()
    res = correlator.correlate(
        deployment_identity="dep-001",
        artifact_digest="sha256:abc123456789",
        release_candidate_id="rc-1.0.0",
        traffic_percentage=100.0,
        observation=obs,
        slo_results=[],
        error_budget_result=None,
        incidents=[],
    )

    assert res.is_healthy is True
    assert res.health_score == 100.0
