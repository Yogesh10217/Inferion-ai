"""Scenario intelligence for baseline, optimistic, pessimistic, best/worst-case modeling."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    ScenarioNotFoundException,
)


class ScenarioType(str, Enum):
    BASELINE = "BASELINE"
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"
    BEST_CASE = "BEST_CASE"
    WORST_CASE = "WORST_CASE"
    CUSTOM = "CUSTOM"


class ScenarioStatus(str, Enum):
    DRAFT = "DRAFT"
    SIMULATED = "SIMULATED"
    EVALUATED = "EVALUATED"
    ARCHIVED = "ARCHIVED"


class ScenarioVariable(BaseModel):
    name: str
    variable_type: str = "numeric"
    baseline_value: Any
    projected_value: Any
    unit: str = ""


class ScenarioAssumption(BaseModel):
    statement: str
    confidence_score: float = 0.8
    source: str = "domain_model"


class ScenarioOutcome(BaseModel):
    metric_name: str
    expected_value: float
    probability: float = 1.0
    impact_description: str = ""


class DecisionScenario(BaseModel):
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    name: str
    description: str = ""
    scenario_type: ScenarioType = ScenarioType.BASELINE
    status: ScenarioStatus = ScenarioStatus.DRAFT
    variables: List[ScenarioVariable] = Field(default_factory=list)
    assumptions: List[ScenarioAssumption] = Field(default_factory=list)
    outcomes: List[ScenarioOutcome] = Field(default_factory=list)
    risk_score: float = 0.0
    confidence_score: float = 0.8
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionScenarioManager:
    """Manages decision scenarios."""

    def __init__(self) -> None:
        self._scenarios: Dict[str, DecisionScenario] = {}

    def create_scenario(
        self,
        tenant_id: str,
        decision_id: str,
        name: str,
        scenario_type: ScenarioType = ScenarioType.BASELINE,
        description: str = "",
        variables: Optional[List[ScenarioVariable]] = None,
        assumptions: Optional[List[ScenarioAssumption]] = None,
        outcomes: Optional[List[ScenarioOutcome]] = None,
        risk_score: float = 0.0,
        confidence_score: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionScenario:
        scenario = DecisionScenario(
            tenant_id=tenant_id,
            decision_id=decision_id,
            name=name,
            scenario_type=scenario_type,
            description=description,
            variables=variables or [],
            assumptions=assumptions or [],
            outcomes=outcomes or [],
            risk_score=risk_score,
            confidence_score=confidence_score,
            metadata=metadata or {},
        )
        self._scenarios[scenario.scenario_id] = scenario
        return scenario

    def get_scenario(self, scenario_id: str, tenant_id: str) -> DecisionScenario:
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ScenarioNotFoundException(f"Scenario '{scenario_id}' not found")
        if scenario.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return scenario

    def list_scenarios_for_decision(self, decision_id: str, tenant_id: str) -> List[DecisionScenario]:
        return [s for s in self._scenarios.values() if s.decision_id == decision_id and s.tenant_id == tenant_id]
