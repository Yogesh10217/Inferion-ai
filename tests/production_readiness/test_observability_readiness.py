from __future__ import annotations

from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.observability_readiness import ObservabilityReleaseEvaluator


def test_observability_readiness_simulation():
    config = RuntimeConfigurationManager().get_config()
    res = ObservabilityReleaseEvaluator.evaluate_observability_readiness(config, is_container_runtime=False)

    assert res.status == "READY"
    assert res.logging_ready is True
    assert "OBSERVABILITY_SIMULATION_VALIDATED" in res.classifications
    assert "OBSERVABILITY_PRODUCTION_RUNTIME_NOT_EXECUTED" in res.classifications


def test_observability_readiness_container():
    config = RuntimeConfigurationManager().get_config()
    res = ObservabilityReleaseEvaluator.evaluate_observability_readiness(config, is_container_runtime=True)

    assert res.status == "READY"
    assert "OBSERVABILITY_CONTAINER_VALIDATED" in res.classifications
    assert "OBSERVABILITY_PRODUCTION_RUNTIME_NOT_EXECUTED" in res.classifications
