"""
Simulation Scenario Generator
"""

from typing import Dict
from pydantic import BaseModel
from app.planning.execution_plan import ExecutionPlan


class Scenario(BaseModel):
    name: str  # optimistic, expected, pessimistic
    duration_multiplier: float
    cost_multiplier: float
    failure_probability: float
    estimated_duration_seconds: float
    estimated_cost: float


class ScenarioGenerator:
    """Generates optimistic, expected, and pessimistic simulation scenarios for a plan."""

    @staticmethod
    def generate_scenarios(plan: ExecutionPlan) -> Dict[str, Scenario]:
        base_dur = plan.estimated_duration_seconds or 10.0
        base_cost = plan.estimated_cost or 0.01

        return {
            "optimistic": Scenario(
                name="optimistic",
                duration_multiplier=0.8,
                cost_multiplier=0.9,
                failure_probability=0.02,
                estimated_duration_seconds=base_dur * 0.8,
                estimated_cost=base_cost * 0.9,
            ),
            "expected": Scenario(
                name="expected",
                duration_multiplier=1.0,
                cost_multiplier=1.0,
                failure_probability=0.05,
                estimated_duration_seconds=base_dur * 1.0,
                estimated_cost=base_cost * 1.0,
            ),
            "pessimistic": Scenario(
                name="pessimistic",
                duration_multiplier=1.8,
                cost_multiplier=1.5,
                failure_probability=0.25,
                estimated_duration_seconds=base_dur * 1.8,
                estimated_cost=base_cost * 1.5,
            ),
        }
