"""Provider-Based What-If Scenario Simulation Engine."""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.intelligence_platform.context import IntelligenceContext
from app.intelligence_platform.exceptions import SimulationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SimulationScenario(str, Enum):
    WHAT_IF = "WHAT_IF"
    CAPACITY = "CAPACITY"
    COST = "COST"
    DEPLOYMENT = "DEPLOYMENT"
    FAILOVER = "FAILOVER"
    REMEDIATION = "REMEDIATION"
    RESOURCE_ALLOCATION = "RESOURCE_ALLOCATION"
    POLICY_CHANGE = "POLICY_CHANGE"


class SimulationInput(BaseModel):
    scenario_name: str
    target_resource_id: str
    action_type: str  # e.g., "ROLLBACK", "SCALE_UP", "MODEL_SWITCH", "POLICY_STRICT"
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SimulationOutcome(BaseModel):
    estimated_cost_impact_usd: float = 0.0
    estimated_latency_impact_ms: float = 0.0
    estimated_risk_delta_pct: float = -20.0
    estimated_availability_pct: float = 99.95
    estimated_recovery_time_seconds: float = 45.0


class SimulationResult(BaseModel):
    simulation_id: str = Field(default_factory=lambda: f"sim_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    scenario: SimulationScenario
    input_parameters: SimulationInput
    outcome: SimulationOutcome = Field(default_factory=SimulationOutcome)
    confidence_score: float = 0.90
    simulation_version: str = "v1.0.0"
    is_production_executed: bool = False  # Always False
    created_at: datetime = Field(default_factory=_now)


class SimulationStrategy(ABC):
    """Abstract interface for simulation strategies."""

    @abstractmethod
    def run_simulation(self, tenant_id: str, scenario: SimulationScenario, input_params: SimulationInput, context: IntelligenceContext) -> SimulationResult:
        pass


class DeterministicSimulationStrategy(SimulationStrategy):
    """Deterministic simulation strategy evaluating simulated delta metrics."""

    def run_simulation(self, tenant_id: str, scenario: SimulationScenario, input_params: SimulationInput, context: IntelligenceContext) -> SimulationResult:
        act = input_params.action_type.upper()

        if "ROLLBACK" in act:
            cost = -10.0
            latency = -45.0
            risk_delta = -35.0
            avail = 99.99
            recovery = 30.0
        elif "SCALE" in act:
            cost = 50.0
            latency = -80.0
            risk_delta = -40.0
            avail = 99.99
            recovery = 60.0
        elif "MODEL_SWITCH" in act:
            cost = -30.0
            latency = 15.0
            risk_delta = -10.0
            avail = 99.90
            recovery = 10.0
        else:
            cost = 0.0
            latency = 0.0
            risk_delta = -15.0
            avail = 99.95
            recovery = 20.0

        outcome = SimulationOutcome(
            estimated_cost_impact_usd=cost,
            estimated_latency_impact_ms=latency,
            estimated_risk_delta_pct=risk_delta,
            estimated_availability_pct=avail,
            estimated_recovery_time_seconds=recovery,
        )

        return SimulationResult(
            tenant_id=tenant_id,
            scenario=scenario,
            input_parameters=input_params,
            outcome=outcome,
            confidence_score=0.92,
            simulation_version="v1.0.0-deterministic",
            is_production_executed=False,
        )


class SimulationEngine:
    """Orchestrates non-production scenario simulations."""

    def __init__(self, strategy: Optional[SimulationStrategy] = None) -> None:
        self.strategy = strategy or DeterministicSimulationStrategy()
        self._simulations: Dict[str, SimulationResult] = {}

    def simulate(self, tenant_id: str, scenario: SimulationScenario, input_params: SimulationInput, context: IntelligenceContext) -> SimulationResult:
        if not tenant_id:
            raise SimulationException("Tenant ID is required for simulation.")

        res = self.strategy.run_simulation(tenant_id, scenario, input_params, context)
        # Invariant check
        if res.is_production_executed:
            raise SimulationException("Simulation MUST NEVER execute in production directly!")

        self._simulations[res.simulation_id] = res
        logger.info(f"[SIMULATION ENGINE] Executed non-production simulation '{res.simulation_id}' for tenant '{tenant_id}'")
        return res

    def get_simulation(self, simulation_id: str, tenant_id: str) -> SimulationResult:
        sim = self._simulations.get(simulation_id)
        if not sim or sim.tenant_id != tenant_id:
            raise SimulationException(f"Simulation '{simulation_id}' not found for tenant '{tenant_id}'.")
        return sim
