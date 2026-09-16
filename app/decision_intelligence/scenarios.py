"""Scenario Planning & Non-Mutating Simulation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import CrossTenantDecisionAccessException, DecisionScenarioException


class ScenarioType(str, Enum):
    BASELINE = "BASELINE"
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"
    RISK_ADJUSTED = "RISK_ADJUSTED"
    COST_OPTIMIZED = "COST_OPTIMIZED"
    RESILIENCE_OPTIMIZED = "RESILIENCE_OPTIMIZED"
    COMPLIANCE_FIRST = "COMPLIANCE_FIRST"
    CUSTOM = "CUSTOM"


class ScenarioStatus(str, Enum):
    DRAFT = "DRAFT"
    SIMULATED = "SIMULATED"
    SELECTED = "SELECTED"
    ARCHIVED = "ARCHIVED"


class ScenarioAssumption(BaseModel):
    name: str
    description: str
    value: Any


class ScenarioVariable(BaseModel):
    name: str
    value: float


class ScenarioOutcome(BaseModel):
    expected_cost_usd: float
    expected_benefit_usd: float
    expected_roi_pct: float
    risk_score: float
    compliance_score: float
    trust_score: float


class DecisionScenario(BaseModel):
    scenario_id: str = Field(default_factory=lambda: f"scen_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    scenario_type: ScenarioType = ScenarioType.BASELINE
    title: str
    assumptions: List[ScenarioAssumption] = Field(default_factory=list)
    variables: List[ScenarioVariable] = Field(default_factory=list)
    simulated_outcome: Optional[ScenarioOutcome] = None
    status: ScenarioStatus = ScenarioStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScenarioManager:
    """Manages creation and non-mutating simulation of decision scenarios."""

    def __init__(self) -> None:
        self._scenarios: Dict[str, DecisionScenario] = {}

    def create_scenario(
        self,
        tenant_id: str,
        context_id: str,
        title: str,
        scenario_type: ScenarioType = ScenarioType.BASELINE,
        assumptions: Optional[List[ScenarioAssumption]] = None,
        variables: Optional[List[ScenarioVariable]] = None,
    ) -> DecisionScenario:
        scen = DecisionScenario(
            tenant_id=tenant_id,
            context_id=context_id,
            title=title,
            scenario_type=scenario_type,
            assumptions=assumptions or [],
            variables=variables or [],
        )
        self._scenarios[scen.scenario_id] = scen
        return scen

    def simulate_scenario(self, scenario_id: str, tenant_id: str) -> DecisionScenario:
        scen = self.get_scenario(scenario_id, tenant_id)

        # Compute non-mutating simulation outcome based on scenario_type
        if scen.scenario_type == ScenarioType.OPTIMISTIC:
            cost = 40000.0
            benefit = 120000.0
            risk = 15.0
            comp = 95.0
        elif scen.scenario_type == ScenarioType.PESSIMISTIC:
            cost = 70000.0
            benefit = 60000.0
            risk = 45.0
            comp = 85.0
        elif scen.scenario_type == ScenarioType.COST_OPTIMIZED:
            cost = 30000.0
            benefit = 80000.0
            risk = 25.0
            comp = 90.0
        else:  # BASELINE
            cost = 50000.0
            benefit = 100000.0
            risk = 20.0
            comp = 90.0

        roi = ((benefit - cost) / max(1.0, cost)) * 100.0
        outcome = ScenarioOutcome(
            expected_cost_usd=cost,
            expected_benefit_usd=benefit,
            expected_roi_pct=roi,
            risk_score=risk,
            compliance_score=comp,
            trust_score=90.0,
        )

        scen.simulated_outcome = outcome
        scen.status = ScenarioStatus.SIMULATED
        return scen

    def get_scenario(self, scenario_id: str, tenant_id: str) -> DecisionScenario:
        scen = self._scenarios.get(scenario_id)
        if not scen:
            raise DecisionScenarioException(f"Scenario '{scenario_id}' not found.")
        if scen.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionAccessException(tenant_id, scen.tenant_id)
        return scen
