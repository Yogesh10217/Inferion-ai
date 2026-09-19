import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.limits.exceptions import QuotaExceededException
from app.limits.models import QuotaPolicy, QuotaWindow
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class QuotaService:
    def __init__(self, session_factory, metrics: MetricsService):
        self.session_factory = session_factory
        self.metrics = metrics

    async def _check_scope_quota(self, session: AsyncSession, scope_type: str, scope_id: str, date_str: str) -> None:
        """Evaluate quotas for a specific scope."""
        # Find policy for this scope
        stmt = select(QuotaPolicy).filter(
            getattr(QuotaPolicy, f"{scope_type}_id") == scope_id, QuotaPolicy.enabled == True
        )
        result = await session.execute(stmt)
        policy = result.scalar_one_or_none()

        # Follow inheritance if applicable
        while policy and policy.parent_policy_id:
            parent_stmt = select(QuotaPolicy).filter(QuotaPolicy.id == policy.parent_policy_id)
            parent_result = await session.execute(parent_stmt)
            parent_policy = parent_result.scalar_one_or_none()
            if not parent_policy:
                break

            # Merge limits (child overrides parent)
            if policy.tokens_per_day is None:
                policy.tokens_per_day = parent_policy.tokens_per_day
            if policy.requests_per_day is None:
                policy.requests_per_day = parent_policy.requests_per_day

            policy = parent_policy

        if not policy:
            return

        window_scope = f"{scope_type}:{scope_id}"

        # Check Tokens
        if policy.tokens_per_day:
            w_stmt = select(QuotaWindow).filter(
                QuotaWindow.scope_id == window_scope,
                QuotaWindow.window_id == date_str,
                QuotaWindow.metric_type == "tokens",
            )
            w_result = await session.execute(w_stmt)
            window = w_result.scalar_one_or_none()

            if window and window.value >= policy.tokens_per_day:
                self.metrics.record_quota_violation()
                raise QuotaExceededException(f"Daily token quota exceeded for {scope_type}")

        # Check Requests
        if policy.requests_per_day:
            w_stmt = select(QuotaWindow).filter(
                QuotaWindow.scope_id == window_scope,
                QuotaWindow.window_id == date_str,
                QuotaWindow.metric_type == "requests",
            )
            w_result = await session.execute(w_stmt)
            window = w_result.scalar_one_or_none()

            if window and window.value >= policy.requests_per_day:
                self.metrics.record_quota_violation()
                raise QuotaExceededException(f"Daily request quota exceeded for {scope_type}")

    async def evaluate_quotas(
        self,
        organization_id: str,
        workspace_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Evaluate quotas hierarchically: Org -> Workspace -> API Key -> User.
        Fails fast if an upper-level quota is exceeded.
        """
        import datetime

        date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

        async with self.session_factory() as session:
            # 1. Organization
            await self._check_scope_quota(session, "organization", organization_id, date_str)

            # 2. Workspace
            if workspace_id:
                await self._check_scope_quota(session, "workspace", workspace_id, date_str)

            # 3. API Key
            if api_key_id:
                await self._check_scope_quota(session, "api_key", api_key_id, date_str)

            # 4. User
            if user_id:
                await self._check_scope_quota(session, "user", user_id, date_str)
