from __future__ import annotations

from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.infrastructure_readiness import InfrastructureReadinessEvaluator
from app.deployment.models import InfrastructureReadinessStatus


def test_infrastructure_readiness_boundaries():
    config = RuntimeConfigurationManager().get_config()
    res = InfrastructureReadinessEvaluator.evaluate_infrastructure_readiness(config, is_container_runtime=False)

    assert res.status == "READY"
    assert res.overall_classification == InfrastructureReadinessStatus.INFRASTRUCTURE_SIMULATION_VALIDATED

    # Verify DNS, TLS, and Cloud boundaries remain NOT_EXECUTED
    req_map = {r.name: r.status for r in res.requirements}
    assert req_map["Production Hostname & Domain (DNS)"] == "NOT_EXECUTED"
    assert req_map["TLS Certificate (HTTPS)"] == "NOT_EXECUTED"
    assert req_map["Production Kubernetes / Cloud Cluster"] == "NOT_EXECUTED"
