"""
Tests for Dependency Resilience Module.
"""

from app.reliability.dependency_resilience import (
    DependencyFailureScenario,
    DependencyResilienceEvaluator,
    DependencyState,
)


def test_dependency_outage_simulation():
    evaluator = DependencyResilienceEvaluator()
    states = {
        "postgresql": DependencyState.UNAVAILABLE,
        "redis": DependencyState.AVAILABLE,
        "prometheus": DependencyState.AVAILABLE,
        "event_bus": DependencyState.AVAILABLE,
        "authentication": DependencyState.AVAILABLE,
        "secret_provider": DependencyState.AVAILABLE,
        "external_apis": DependencyState.AVAILABLE,
    }
    scenarios = [DependencyFailureScenario("postgres_fallback", "postgresql", DependencyState.UNAVAILABLE, True, 30.0)]
    res = evaluator.evaluate_dependencies(dependency_states=states, scenarios=scenarios)
    assert res.overall_resilience_score > 0.0
    assert "postgresql" not in res.unhandled_dependencies
