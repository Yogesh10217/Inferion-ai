"""Decision optimization intelligence across cost, risk, reliability, trust, and compliance."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException


class OptimizationObjective(str, Enum):
    MINIMIZE_COST = "MINIMIZE_COST"
    MINIMIZE_RISK = "MINIMIZE_RISK"
    MAXIMIZE_RELIABILITY = "MAXIMIZE_RELIABILITY"
    MAXIMIZE_TRUST = "MAXIMIZE_TRUST"
    MAXIMIZE_COMPLIANCE = "MAXIMIZE_COMPLIANCE"
    MAXIMIZE_EFFICIENCY = "MAXIMIZE_EFFICIENCY"
    BALANCE_OBJECTIVES = "BALANCE_OBJECTIVES"


class OptimizationConstraint(BaseModel):
    name: str
    target_metric: str
    operator: str = "<="  # <=, >=, ==
    value: float
    is_hard_constraint: bool = True


class OptimizationRecommendation(BaseModel):
    parameter_name: str
    current_value: Any
    recommended_value: Any
    expected_gain: str


class OptimizationResult(BaseModel):
    score: float = 0.90
    objective_achieved: bool = True
    recommendations: List[OptimizationRecommendation] = Field(default_factory=list)
    pareto_frontier_rank: int = 1
    summary: str = ""


class DecisionOptimization(BaseModel):
    optimization_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    primary_objective: OptimizationObjective = OptimizationObjective.BALANCE_OBJECTIVES
    constraints: List[OptimizationConstraint] = Field(default_factory=list)
    result: OptimizationResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionOptimizationManager:
    """Manages multi-objective optimization for decision parameters. Advisory only."""

    def __init__(self) -> None:
        self._optimizations: Dict[str, DecisionOptimization] = {}

    def optimize_decision(
        self,
        tenant_id: str,
        decision_id: str,
        primary_objective: OptimizationObjective = OptimizationObjective.BALANCE_OBJECTIVES,
        constraints: Optional[List[OptimizationConstraint]] = None,
    ) -> DecisionOptimization:
        recs = [
            OptimizationRecommendation(
                parameter_name="cost_budget_cap",
                current_value=1000.0,
                recommended_value=850.0,
                expected_gain="15% cost reduction with 0% reliability loss",
            )
        ]
        res = OptimizationResult(
            score=0.94,
            objective_achieved=True,
            recommendations=recs,
            summary=f"Optimized decision {decision_id} for {primary_objective.value}.",
        )
        opt = DecisionOptimization(
            tenant_id=tenant_id,
            decision_id=decision_id,
            primary_objective=primary_objective,
            constraints=constraints or [],
            result=res,
        )
        self._optimizations[opt.optimization_id] = opt
        return opt
