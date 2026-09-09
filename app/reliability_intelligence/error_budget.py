"""Error budget engine for Reliability Intelligence (Phase 5.55)."""

import logging
from typing import Dict, Any
from app.reliability_intelligence.models import ErrorBudget, ErrorBudgetStatus

logger = logging.getLogger(__name__)


class ErrorBudgetEngine:
    """Tracks error budget consumption, burn rate, and predictive exhaustion analysis."""

    def evaluate_error_budget(
        self, tenant_id: str, slo_id: str, total_minutes: float = 43.2, burn_rate: float = 1.0
    ) -> ErrorBudget:
        consumed = min(total_minutes, 5.0 * burn_rate)
        remaining = max(0.0, total_minutes - consumed)
        rem_pct = (remaining / total_minutes) * 100.0

        if rem_pct > 50.0:
            status = ErrorBudgetStatus.HEALTHY
        elif rem_pct > 20.0:
            status = ErrorBudgetStatus.CONSUMING
        elif rem_pct > 0.0:
            status = ErrorBudgetStatus.AT_RISK
        else:
            status = ErrorBudgetStatus.EXHAUSTED

        budget = ErrorBudget(
            slo_id=slo_id,
            tenant_id=tenant_id,
            total_budget_minutes=total_minutes,
            remaining_budget_minutes=round(remaining, 2),
            status=status,
            burn_rate=burn_rate,
        )

        logger.info(f"Evaluated ErrorBudget for SLO '{slo_id}' -> Remaining: {remaining:.2f}m ({status.value})")
        return budget
