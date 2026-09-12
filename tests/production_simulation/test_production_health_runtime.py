import pytest
from app.deployment.deployment_simulation import ProductionSimulationEngine
from app.deployment.models import HealthStatus


def test_production_simulation_health_probes():
    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation()

    probes = evidence.probe_results
    assert probes["live"]["status_code"] == 200
    assert probes["live"]["alive"] is True
    assert probes["live"]["dependencies_required"] is False

    assert probes["ready"]["status_code"] == 200
    assert probes["ready"]["ready"] is True
    assert probes["ready"]["managers_registered"] == 9

    assert probes["health"]["status_code"] == 200
    assert probes["health"]["status"] == HealthStatus.HEALTHY.value
