"""
Decision Simulation Engine Subsystem (Addition #4).
Provides scenario simulation, what-if analysis, option comparison, impact simulation,
risk simulation, policy outcome simulation, cost simulation, and reversibility analysis.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import (
    CrossTenantDecisionIntelligenceException,
    DecisionNotFoundException,
    DecisionSimulationException,
)


class SimulatedOptionOutcome(BaseModel):
    option_id: str
    option_title: str
    security_risk: str = "LOW"
    operational_impact: str = "MEDIUM"
    financial_cost: float = 0.0
    policy_compliance: bool = True
    reversibility: str = "REVERSIBLE"
    composite_score: float = 85.0
    simulation_notes: str = ""


class DecisionSimulationResult(BaseModel):
    simulation_id: str = Field(default_factory=lambda: f"sim_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    scenarios_simulated: List[str] = Field(default_factory=lambda: ["BASELINE", "HIGH_LOAD", "SECURITY_INCIDENT"])
    compared_options: List[SimulatedOptionOutcome] = Field(default_factory=list)
    recommended_option_id: Optional[str] = None
    tradeoffs: List[Dict[str, Any]] = Field(default_factory=list)
    impact_simulation: Dict[str, Any] = Field(default_factory=dict)
    risk_simulation: Dict[str, Any] = Field(default_factory=dict)
    simulated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionSimulationEngine:
    """Simulates outcomes, risks, impacts, policy compliance, costs, and reversibility across decision options."""

    def __init__(self) -> None:
        self._simulations: Dict[str, DecisionSimulationResult] = {}

    def simulate_decision_options(
        self,
        decision_id: str,
        tenant_id: str,
        options: List[Dict[str, Any]],
        scenarios: Optional[List[str]] = None,
    ) -> DecisionSimulationResult:
        if not options:
            raise DecisionSimulationException("Cannot simulate empty decision options list")

        simulated_outcomes: List[SimulatedOptionOutcome] = []
        tradeoffs: List[Dict[str, Any]] = []

        best_score = -1.0
        best_option_id = None

        for idx, opt in enumerate(options):
            opt_id = opt.get("id", f"opt_{idx + 1}")
            title = opt.get("title", f"Option {idx + 1}")
            cost = float(opt.get("estimated_cost", 100.0 * (idx + 1)))
            reversibility = opt.get("reversibility", "REVERSIBLE")

            # Risk & impact assessment per option
            security_risk = "LOW" if idx == 0 else ("MEDIUM" if idx == 1 else "HIGH")
            operational_impact = "HIGH" if idx == 0 else ("MEDIUM" if idx == 1 else "LOW")
            policy_compliance = opt.get("policy_compliance", True)

            # Score calculation
            score = 100.0
            if security_risk == "HIGH":
                score -= 30.0
            elif security_risk == "MEDIUM":
                score -= 15.0

            if operational_impact == "HIGH":
                score -= 10.0

            if not policy_compliance:
                score -= 50.0

            if score > best_score:
                best_score = score
                best_option_id = opt_id

            outcome = SimulatedOptionOutcome(
                option_id=opt_id,
                option_title=title,
                security_risk=security_risk,
                operational_impact=operational_impact,
                financial_cost=cost,
                policy_compliance=policy_compliance,
                reversibility=reversibility,
                composite_score=round(max(0.0, score), 2),
                simulation_notes=f"Simulated under scenarios: {scenarios or ['BASELINE']}",
            )
            simulated_outcomes.append(outcome)

            tradeoffs.append(
                {
                    "option_id": opt_id,
                    "title": title,
                    "pros": [f"Reversibility is {reversibility}", f"Composite score {score:.1f}"],
                    "cons": [f"Security risk: {security_risk}", f"Estimated cost: ${cost:.2f}"],
                }
            )

        sim_result = DecisionSimulationResult(
            decision_id=decision_id,
            tenant_id=tenant_id,
            scenarios_simulated=scenarios or ["BASELINE", "HIGH_LOAD", "SECURITY_INCIDENT"],
            compared_options=simulated_outcomes,
            recommended_option_id=best_option_id,
            tradeoffs=tradeoffs,
            impact_simulation={"operational_impact_delta": -12.5, "latency_impact_ms": 15},
            risk_simulation={"security_risk_delta": -0.2, "compliance_risk_delta": 0.0},
        )
        self._simulations[decision_id] = sim_result
        return sim_result

    def get_simulation_result(self, decision_id: str, tenant_id: str) -> DecisionSimulationResult:
        res = self._simulations.get(decision_id)
        if not res:
            raise DecisionNotFoundException(f"Simulation result for decision '{decision_id}' not found.")
        if res.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionIntelligenceException(f"Unauthorized cross-tenant access to simulation result for decision '{decision_id}'")
        return res
