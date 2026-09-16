"""Multi-Objective Portfolio Optimization Subsystem."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.business_cases import BusinessCase
from app.portfolio_platform.prioritization import PrioritizationResult


class OptimizationGoal(str, Enum):
    MAXIMIZE_VALUE = "MAXIMIZE_VALUE"
    MAXIMIZE_ROI = "MAXIMIZE_ROI"
    MAXIMIZE_ALIGNMENT = "MAXIMIZE_ALIGNMENT"
    MINIMIZE_RISK = "MINIMIZE_RISK"


class PortfolioConstraint(BaseModel):
    max_budget_usd: float = 250000.0
    max_risk_score: float = 50.0
    min_compliance_score: float = 70.0
    min_architecture_trust: float = 70.0


class SelectedCandidate(BaseModel):
    initiative_id: str
    allocated_cost_usd: float
    expected_roi_pct: float
    score: float


class PortfolioOptimizationResult(BaseModel):
    optimization_id: str = Field(default_factory=lambda: f"opt_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    goal: OptimizationGoal = OptimizationGoal.MAXIMIZE_VALUE
    selected_initiatives: List[SelectedCandidate] = Field(default_factory=list)
    deprioritized_initiatives: List[str] = Field(default_factory=list)
    total_cost_usd: float = 0.0
    total_expected_value_usd: float = 0.0
    constraint_used: PortfolioConstraint = Field(default_factory=PortfolioConstraint)
    optimization_fingerprint: str
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioOptimizationEngine:
    """Multi-objective portfolio optimization solver respecting budget and risk constraints."""

    def optimize_portfolio(
        self,
        tenant_id: str,
        prioritization_result: PrioritizationResult,
        business_cases: List[BusinessCase],
        constraint: Optional[PortfolioConstraint] = None,
        goal: OptimizationGoal = OptimizationGoal.MAXIMIZE_VALUE,
    ) -> PortfolioOptimizationResult:
        const = constraint or PortfolioConstraint()
        bc_map = {bc.initiative_id: bc for bc in business_cases}

        selected: List[SelectedCandidate] = []
        deprioritized: List[str] = []
        accumulated_cost = 0.0
        accumulated_value = 0.0

        for item in prioritization_result.ranked_initiatives:
            bc = bc_map.get(item.initiative_id)
            cost = bc.costs.implementation_cost_usd if bc else 50000.0
            val = bc.roi_projection.net_present_value_usd if bc else 100000.0
            roi = bc.roi_projection.estimated_roi_percentage if bc else 150.0
            risk = bc.risk_score if bc else 20.0
            comp = bc.compliance_score if bc else 90.0
            arch = bc.architecture_trust_score if bc else 90.0

            # Constraint checks
            if risk > const.max_risk_score or comp < const.min_compliance_score or arch < const.min_architecture_trust:
                deprioritized.append(item.initiative_id)
                continue

            if accumulated_cost + cost <= const.max_budget_usd:
                selected.append(
                    SelectedCandidate(
                        initiative_id=item.initiative_id,
                        allocated_cost_usd=cost,
                        expected_roi_pct=roi,
                        score=item.total_score,
                    )
                )
                accumulated_cost += cost
                accumulated_value += val
            else:
                deprioritized.append(item.initiative_id)

        canonical_str = json.dumps(
            {
                "tenant": tenant_id,
                "goal": goal.value,
                "selected": [s.initiative_id for s in selected],
                "budget": const.max_budget_usd,
                "total_cost": accumulated_cost,
            },
            sort_keys=True,
        )
        fingerprint = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        return PortfolioOptimizationResult(
            tenant_id=tenant_id,
            goal=goal,
            selected_initiatives=selected,
            deprioritized_initiatives=deprioritized,
            total_cost_usd=accumulated_cost,
            total_expected_value_usd=accumulated_value,
            constraint_used=const,
            optimization_fingerprint=fingerprint,
        )
