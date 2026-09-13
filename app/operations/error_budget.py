"""
Error Budget Engine for Phase 5.68.
Calculates and tracks total, consumed, and remaining error budget without allowing negative budgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.slo import SLOResult, SLOStatus, SLIType


class ErrorBudgetStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EXHAUSTED = "EXHAUSTED"
    NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"


@dataclass
class ErrorBudget:
    total_budget: float
    consumed_budget: float
    remaining_budget: float
    consumption_percentage: float
    status: ErrorBudgetStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_budget": self.total_budget,
            "consumed_budget": self.consumed_budget,
            "remaining_budget": self.remaining_budget,
            "consumption_percentage": self.consumption_percentage,
            "status": self.status.value,
        }


@dataclass
class ErrorBudgetResult:
    status: ErrorBudgetStatus
    budget: ErrorBudget
    evidence_level: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "budget": self.budget.to_dict(),
            "evidence_level": self.evidence_level,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class ErrorBudgetEvaluator:
    """Evaluates consumed and remaining error budgets across SLO evaluations."""

    def __init__(self, default_total_budget: float = 100.0) -> None:
        self.default_total_budget = default_total_budget

    def evaluate(self, slo_results: List[SLOResult], evidence_level: str = "CONTAINER_RUNTIME") -> ErrorBudgetResult:
        if not slo_results:
            budget = ErrorBudget(
                total_budget=self.default_total_budget,
                consumed_budget=0.0,
                remaining_budget=self.default_total_budget,
                consumption_percentage=0.0,
                status=ErrorBudgetStatus.NOT_ENOUGH_DATA,
            )
            return ErrorBudgetResult(
                status=ErrorBudgetStatus.NOT_ENOUGH_DATA,
                budget=budget,
                evidence_level=evidence_level,
                details={"reason": "No SLO results provided"},
            )

        # Calculate error budget consumption based on availability and error rate SLOs
        consumed = 0.0
        for slo_res in slo_results:
            slo = slo_res.slo
            obs = slo_res.observed_value
            if slo.sli_type == SLIType.AVAILABILITY:
                # Target is e.g. 0.999 (0.1% allowed error)
                allowed_error = max(0.0001, 1.0 - slo.target_value)
                actual_error = max(0.0, 1.0 - obs)
                consumed_fraction = actual_error / allowed_error
                consumed += min(100.0, consumed_fraction * 100.0)
            elif slo.sli_type == SLIType.ERROR_RATE:
                allowed_error = slo.target_value
                actual_error = obs
                consumed_fraction = actual_error / allowed_error if allowed_error > 0 else 1.0
                consumed += min(100.0, consumed_fraction * 100.0)

        # Cap consumed to total budget
        total = self.default_total_budget
        consumed = max(0.0, min(total, consumed))
        remaining = max(0.0, total - consumed)
        consumption_pct = (consumed / total * 100.0) if total > 0 else 0.0

        if remaining == 0.0 or consumption_pct >= 100.0:
            status = ErrorBudgetStatus.EXHAUSTED
        elif consumption_pct >= 80.0:
            status = ErrorBudgetStatus.CRITICAL
        elif consumption_pct >= 50.0:
            status = ErrorBudgetStatus.WARNING
        else:
            status = ErrorBudgetStatus.HEALTHY

        budget = ErrorBudget(
            total_budget=total,
            consumed_budget=consumed,
            remaining_budget=remaining,
            consumption_percentage=round(consumption_pct, 2),
            status=status,
        )

        return ErrorBudgetResult(
            status=status,
            budget=budget,
            evidence_level=evidence_level,
            details={
                "total_budget": total,
                "consumed_budget": consumed,
                "remaining_budget": remaining,
                "consumption_pct": consumption_pct,
            },
        )
