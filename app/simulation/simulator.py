"""
Plan Execution Simulator Engine
"""

import logging
import time
from typing import Any, Dict

from app.planning.execution_plan import ExecutionPlan
from app.simulation.risk_engine import RiskEngine
from app.simulation.scenario_generator import ScenarioGenerator

logger = logging.getLogger(__name__)


class ExecutionSimulator:
    """Simulates plan execution across scenarios and provides probabilistic impact forecasts."""

    def simulate_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        start_t = time.time()
        scenarios = ScenarioGenerator.generate_scenarios(plan)
        risks = RiskEngine.analyze_plan_risks(plan)

        avg_failure_prob = sum(s.failure_probability for s in scenarios.values()) / float(len(scenarios))
        exp_scenario = scenarios["expected"]

        return {
            "plan_id": plan.plan_id,
            "status": "simulated",
            "simulation_time_seconds": time.time() - start_t,
            "expected_cost": exp_scenario.estimated_cost,
            "expected_duration_seconds": exp_scenario.estimated_duration_seconds,
            "average_failure_probability": avg_failure_prob,
            "scenarios": {k: v.model_dump() for k, v in scenarios.items()},
            "risk_factors": [r.model_dump() for r in risks],
        }
