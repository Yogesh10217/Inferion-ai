from typing import Optional

from sqlalchemy import select

from app.billing.exceptions import BudgetExceededException
from app.billing.models import Budget
from app.services.metrics_service import MetricsService


class BudgetService:
    def __init__(self, session_factory, metrics_service: MetricsService):
        self.session_factory = session_factory
        self.metrics = metrics_service
        # In a real distributed system, we would use Redis to store current real-time spend.
        # For this implementation, we use an in-memory dictionary.
        self._current_spend: dict[str, float] = {}

    async def get_budget(self, org_id: str, workspace_id: Optional[str] = None) -> Optional[Budget]:
        stmt = select(Budget).where(Budget.organization_id == org_id, Budget.enabled == True)
        if workspace_id:
            stmt = stmt.where(Budget.workspace_id == workspace_id)
        else:
            stmt = stmt.where(Budget.workspace_id.is_(None))

        async with self.session_factory() as db:
            result = await db.execute(stmt)
            return result.scalars().first()

    async def create_or_update_budget(
        self, org_id: str, workspace_id: Optional[str], hard_limit: float, warning: float = 0.0, critical: float = 0.0
    ) -> Budget:
        async with self.session_factory() as db:
            stmt = select(Budget).where(Budget.organization_id == org_id, Budget.enabled == True)
            if workspace_id:
                stmt = stmt.where(Budget.workspace_id == workspace_id)
            else:
                stmt = stmt.where(Budget.workspace_id.is_(None))

            result = await db.execute(stmt)
            budget = result.scalars().first()

            if not budget:
                budget = Budget(organization_id=org_id, workspace_id=workspace_id)
                db.add(budget)

            budget.hard_limit = hard_limit
            budget.warning_threshold = warning
            budget.critical_threshold = critical
            budget.enabled = True

            await db.commit()
            await db.refresh(budget)
            return budget

    async def check_budget_limit(self, org_id: str, workspace_id: Optional[str] = None) -> None:
        """
        Fast O(1) check using cached spend values.
        Throws BudgetExceededException if hard limit is breached.
        """
        budget = await self.get_budget(org_id, workspace_id)
        if not budget or not budget.enabled or budget.hard_limit == 0.0:
            return

        cache_key = f"{org_id}:{workspace_id or 'none'}"
        current_spend = self._current_spend.get(cache_key, 0.0)

        if current_spend >= budget.hard_limit:
            self.metrics.record_budget_violation()
            raise BudgetExceededException(f"Organization {org_id} exceeded budget hard limit of {budget.hard_limit}")

        if budget.critical_threshold > 0.0 and current_spend >= budget.critical_threshold:
            self.metrics.record_budget_warning()
        elif budget.warning_threshold > 0.0 and current_spend >= budget.warning_threshold:
            self.metrics.record_budget_warning()

    def update_spend_cache(self, org_id: str, workspace_id: Optional[str], spend_delta: float) -> None:
        """Called by a background worker or UsageService listener to update current spend in memory/Redis."""
        cache_key = f"{org_id}:{workspace_id or 'none'}"
        self._current_spend[cache_key] = self._current_spend.get(cache_key, 0.0) + spend_delta
