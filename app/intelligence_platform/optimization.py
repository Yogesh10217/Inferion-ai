"""Multi-Objective Optimization Engine with Solver Abstraction."""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.intelligence_platform.exceptions import OptimizationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OptimizationObjective(str, Enum):
    MINIMIZE_COST = "MINIMIZE_COST"
    MINIMIZE_LATENCY = "MINIMIZE_LATENCY"
    MAXIMIZE_RELIABILITY = "MAXIMIZE_RELIABILITY"
    MAXIMIZE_QUALITY = "MAXIMIZE_QUALITY"
    MINIMIZE_RISK = "MINIMIZE_RISK"
    MINIMIZE_CARBON = "MINIMIZE_CARBON"
    MAXIMIZE_THROUGHPUT = "MAXIMIZE_THROUGHPUT"


class OptimizationConstraint(BaseModel):
    max_cost_usd: Optional[float] = None
    max_latency_ms: Optional[float] = None
    max_allowed_risk: str = "HIGH"
    enforce_governance_policy: bool = True  # Invariant: Never silently bypass governance


class OptimizationCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: f"cand_{uuid.uuid4().hex[:10]}")
    name: str
    action_type: str
    target_resource_id: str
    cost_usd: float
    latency_ms: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    reliability_score: float = 0.95
    score: float = 0.0


class OptimizationResult(BaseModel):
    optimization_id: str = Field(default_factory=lambda: f"opt_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    objective: OptimizationObjective
    candidates_evaluated: int
    winning_candidate: OptimizationCandidate
    all_candidates: List[OptimizationCandidate] = Field(default_factory=list)
    solver_name: str = "ParetoOptimizationSolver"
    evaluated_at: datetime = Field(default_factory=_now)


class OptimizationSolver(ABC):
    """Abstract interface for optimization solvers."""

    @abstractmethod
    def solve(
        self,
        tenant_id: str,
        objective: OptimizationObjective,
        candidates: List[OptimizationCandidate],
        constraint: OptimizationConstraint,
    ) -> OptimizationResult:
        pass


class ParetoOptimizationSolver(OptimizationSolver):
    """Pareto-frontier multi-objective optimization solver."""

    def solve(
        self,
        tenant_id: str,
        objective: OptimizationObjective,
        candidates: List[OptimizationCandidate],
        constraint: OptimizationConstraint,
    ) -> OptimizationResult:
        if not candidates:
            raise OptimizationException("Optimization requires at least one candidate option.")

        valid_candidates = []
        for cand in candidates:
            # Enforce hard constraints
            if constraint.max_cost_usd is not None and cand.cost_usd > constraint.max_cost_usd:
                continue
            if constraint.max_latency_ms is not None and cand.latency_ms > constraint.max_latency_ms:
                continue

            # Governance check
            if constraint.enforce_governance_policy and cand.risk_level == "CRITICAL":
                continue

            # Compute score based on objective
            if objective == OptimizationObjective.MINIMIZE_COST:
                cand.score = 100.0 - cand.cost_usd
            elif objective == OptimizationObjective.MINIMIZE_LATENCY:
                cand.score = 1000.0 - cand.latency_ms
            elif objective == OptimizationObjective.MINIMIZE_RISK:
                risk_weights = {"LOW": 100, "MEDIUM": 70, "HIGH": 30, "CRITICAL": 0}
                cand.score = risk_weights.get(cand.risk_level, 50)
            else:
                cand.score = (cand.reliability_score * 100) - cand.cost_usd

            valid_candidates.append(cand)

        if not valid_candidates:
            # Fallback to candidates meeting hard security bounds
            valid_candidates = [c for c in candidates if c.risk_level != "CRITICAL"]
            if not valid_candidates:
                raise OptimizationException("No candidates satisfied optimization security and governance constraints.")

        valid_candidates.sort(key=lambda c: c.score, reverse=True)
        winner = valid_candidates[0]

        return OptimizationResult(
            tenant_id=tenant_id,
            objective=objective,
            candidates_evaluated=len(candidates),
            winning_candidate=winner,
            all_candidates=valid_candidates,
            solver_name="ParetoOptimizationSolver",
        )


class OptimizationEngine:
    """Orchestrates candidate optimization."""

    def __init__(self, solver: Optional[OptimizationSolver] = None) -> None:
        self.solver = solver or ParetoOptimizationSolver()
        self._results: Dict[str, OptimizationResult] = {}

    def optimize(
        self,
        tenant_id: str,
        objective: OptimizationObjective,
        candidates: List[OptimizationCandidate],
        constraint: Optional[OptimizationConstraint] = None,
    ) -> OptimizationResult:
        if not tenant_id:
            raise OptimizationException("Tenant ID is required for optimization.")

        res = self.solver.solve(tenant_id, objective, candidates, constraint or OptimizationConstraint())
        self._results[res.optimization_id] = res
        logger.info(
            f"[OPTIMIZATION ENGINE] Executed optimization '{res.optimization_id}' for tenant '{tenant_id}' (Winner: '{res.winning_candidate.name}')"
        )
        return res

    def get_result(self, optimization_id: str, tenant_id: str) -> OptimizationResult:
        res = self._results.get(optimization_id)
        if not res or res.tenant_id != tenant_id:
            raise OptimizationException(f"Optimization '{optimization_id}' not found for tenant '{tenant_id}'.")
        return res
