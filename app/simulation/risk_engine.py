"""
Risk Analysis Engine for Plan Execution
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.planning.execution_plan import ExecutionPlan

logger = logging.getLogger(__name__)


class RiskFactor(BaseModel):
    risk_id: str
    category: str
    severity: str  # low, medium, high, critical
    probability: float
    description: str
    mitigation: str


class RiskEngine:
    """Analyzes, ranks, and recommends mitigations for execution risks."""

    @staticmethod
    def analyze_plan_risks(plan: ExecutionPlan) -> List[RiskFactor]:
        risks = []
        if plan.estimated_cost > 10.0:
            risks.append(RiskFactor(
                risk_id="risk_cost_overrun",
                category="financial",
                severity="medium",
                probability=0.20,
                description=f"Plan estimated cost ${plan.estimated_cost:.2f} exceeds standard single-run baseline",
                mitigation="Enable strict per-step budget caps and approval gates",
            ))

        if len(plan.tasks) > 5:
            risks.append(RiskFactor(
                risk_id="risk_complexity",
                category="execution",
                severity="low",
                probability=0.15,
                description=f"Plan has {len(plan.tasks)} tasks, increasing coordination complexity",
                mitigation="Decompose into parallel sub-teams or sub-workflows",
            ))

        # Default low baseline risk
        if not risks:
            risks.append(RiskFactor(
                risk_id="risk_baseline",
                category="operational",
                severity="low",
                probability=0.05,
                description="Standard operational execution risk",
                mitigation="Monitor execution steps via supervisor agent",
            ))

        logger.info(f"[RISK ENGINE] Identified {len(risks)} risk factors for plan '{plan.plan_id}'")
        return risks
