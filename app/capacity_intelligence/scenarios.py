"""What-if capacity scenario engine for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import CapacityScenario

logger = logging.getLogger(__name__)


class CapacityScenarioEngine:
    """Runs what-if capacity simulations without executing infrastructure mutations."""

    def simulate_scenario(
        self, tenant_id: str, scenario_name: str, workload_multiplier: float = 2.0, base_headroom_pct: float = 40.0
    ) -> CapacityScenario:
        sim_headroom = max(0.0, base_headroom_pct - ((workload_multiplier - 1.0) * 30.0))
        is_feasible = sim_headroom > 10.0

        scen = CapacityScenario(
            tenant_id=tenant_id,
            scenario_name=scenario_name,
            workload_multiplier=workload_multiplier,
            simulated_headroom_pct=round(sim_headroom, 2),
            is_feasible=is_feasible,
        )
        logger.info(f"Simulated CapacityScenario '{scenario_name}' (Multiplier: {workload_multiplier}x, Headroom: {sim_headroom}%, Feasible: {is_feasible})")
        return scen
