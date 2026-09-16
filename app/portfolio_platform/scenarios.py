"""Portfolio Scenario Simulation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.optimization import (
    OptimizationGoal,
    PortfolioConstraint,
    PortfolioOptimizationEngine,
    PortfolioOptimizationResult,
)
from app.portfolio_platform.prioritization import PrioritizationResult


class ScenarioType(str, Enum):
    BUDGET_REDUCTION = "BUDGET_REDUCTION"
    BUDGET_INCREASE = "BUDGET_INCREASE"
    INITIATIVE_DELAY = "INITIATIVE_DELAY"
    COMPLIANCE_BLOCK = "COMPLIANCE_BLOCK"
    CAPACITY_CONSTRAINT = "CAPACITY_CONSTRAINT"


class ScenarioAssumption(BaseModel):
    parameter: str  # e.g., budget_reduction_percentage
    value: float = 20.0


class PortfolioScenario(BaseModel):
    scenario_id: str = Field(default_factory=lambda: f"scen_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    scenario_type: ScenarioType
    description: str
    assumptions: List[ScenarioAssumption] = Field(default_factory=list)
    simulated_result: Optional[PortfolioOptimizationResult] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioScenarioManager:
    """Simulates portfolio scenario outcomes without mutating production state."""

    def __init__(self, optimization_engine: Optional[PortfolioOptimizationEngine] = None) -> None:
        self.optimization_engine = optimization_engine or PortfolioOptimizationEngine()

    def simulate_budget_reduction(
        self,
        tenant_id: str,
        prioritization_result: PrioritizationResult,
        business_cases: List[Any],
        baseline_budget_usd: float = 250000.0,
        reduction_percentage: float = 20.0,
    ) -> PortfolioScenario:
        reduced_budget = baseline_budget_usd * (1.0 - (reduction_percentage / 100.0))
        constraint = PortfolioConstraint(max_budget_usd=reduced_budget)

        # Run optimization on reduced budget (non-mutating simulation)
        opt_res = self.optimization_engine.optimize_portfolio(
            tenant_id=tenant_id,
            prioritization_result=prioritization_result,
            business_cases=business_cases,
            constraint=constraint,
            goal=OptimizationGoal.MAXIMIZE_VALUE,
        )

        scenario = PortfolioScenario(
            tenant_id=tenant_id,
            scenario_type=ScenarioType.BUDGET_REDUCTION,
            description=f"Simulated {reduction_percentage}% budget reduction to ${reduced_budget:,.2f}.",
            assumptions=[ScenarioAssumption(parameter="reduction_percentage", value=reduction_percentage)],
            simulated_result=opt_res,
        )
        return scenario
