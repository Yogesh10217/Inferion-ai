"""Unit tests for Provider-Based What-If Scenario Simulation Engine."""

from app.intelligence_platform.context import ContextBuilder
from app.intelligence_platform.simulation import (
    DeterministicSimulationStrategy,
    SimulationEngine,
    SimulationInput,
    SimulationScenario,
)


def test_simulation_never_executes_in_production():
    ctx = ContextBuilder().assemble_context("t1", primary_resource_id="gateway_prod")
    engine = SimulationEngine(strategy=DeterministicSimulationStrategy())

    sim_input = SimulationInput(
        scenario_name="Rollback_Check", target_resource_id="gateway_prod", action_type="ROLLBACK"
    )
    res = engine.simulate("t1", SimulationScenario.FAILOVER, sim_input, ctx)

    assert res.simulation_id.startswith("sim_")
    assert res.is_production_executed is False
    assert res.outcome.estimated_cost_impact_usd < 0
