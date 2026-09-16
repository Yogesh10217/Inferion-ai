"""Non-Mutating Architecture Change Simulation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.architecture_platform.impact import ImpactAnalyzer


class SimulationScenario(str, Enum):
    SERVICE_REMOVAL = "SERVICE_REMOVAL"
    MODEL_REPLACEMENT = "MODEL_REPLACEMENT"
    AGENT_REPLACEMENT = "AGENT_REPLACEMENT"
    WORKFLOW_MODIFICATION = "WORKFLOW_MODIFICATION"
    INTEGRATION_FAILURE = "INTEGRATION_FAILURE"
    DATA_SOURCE_MIGRATION = "DATA_SOURCE_MIGRATION"
    REGIONAL_FAILURE = "REGIONAL_FAILURE"
    TRAFFIC_SPIKE = "TRAFFIC_SPIKE"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    POLICY_CHANGE = "POLICY_CHANGE"


class SimulationResult(BaseModel):
    simulation_id: str = Field(default_factory=lambda: f"sim_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    scenario: SimulationScenario
    target_node_id: str
    predicted_blast_radius_count: int
    predicted_latency_impact_ms: float = 15.0
    predicted_reliability_impact: str = "SLIGHT_DEGRADATION"
    predicted_cost_delta_usd: float = 0.0
    predicted_risk_level: str = "MEDIUM"
    confidence_score: float = 90.0
    assumptions: List[str] = Field(default_factory=list)
    simulated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureSimulation(BaseModel):
    simulation: SimulationResult


class ArchitectureSimulationEngine:
    """Simulates architecture changes without mutating production state."""

    def __init__(self, impact_analyzer: ImpactAnalyzer) -> None:
        self.impact_analyzer = impact_analyzer

    def run_simulation(
        self,
        tenant_id: str,
        target_node_id: str,
        scenario: SimulationScenario = SimulationScenario.MODEL_REPLACEMENT,
    ) -> SimulationResult:
        impact = self.impact_analyzer.analyze_impact(tenant_id, target_node_id, action_type=scenario.value)
        blast_count = impact.blast_radius.total_affected_count

        assumptions = [
            "Simulation is non-mutating and predictive based on dependency graph.",
            f"Assumes 99.9% upstream availability during scenario '{scenario.value}'.",
        ]

        cost_delta = -15.0 if scenario == SimulationScenario.MODEL_REPLACEMENT else 25.0 * blast_count

        return SimulationResult(
            tenant_id=tenant_id,
            scenario=scenario,
            target_node_id=target_node_id,
            predicted_blast_radius_count=blast_count,
            predicted_latency_impact_ms=10.0 * blast_count,
            predicted_reliability_impact="HIGH_RISK" if blast_count > 5 else "STABLE",
            predicted_cost_delta_usd=cost_delta,
            predicted_risk_level=impact.reliability_risk,
            confidence_score=92.5,
            assumptions=assumptions,
        )
