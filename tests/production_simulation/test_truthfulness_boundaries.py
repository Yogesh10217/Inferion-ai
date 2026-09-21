from app.deployment.deployment_simulation import ProductionSimulationEngine
from app.deployment.models import PlatformReadinessClassification


def test_truthfulness_boundaries_enforced():
    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation()

    # Must be PRODUCTION_SIMULATION_VALIDATED
    assert evidence.readiness_classification == PlatformReadinessClassification.PRODUCTION_SIMULATION_VALIDATED

    # Must NOT claim live production statuses
    assert evidence.readiness_classification.value not in (
        "PRODUCTION_DEPLOYED",
        "PRODUCTION_DEPLOYMENT_VALIDATED",
        "PRODUCTION_RUNTIME_VALIDATED",
        "LIVE_PRODUCTION_VALIDATED",
        "LIVE_PRODUCTION_DEPLOYED",
    )
