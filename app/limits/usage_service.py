import asyncio
import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.limits.events import UsageEvent, UsageEventEmitter
from app.limits.models import QuotaWindow, UsageRecord
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class UsageService(UsageEventEmitter):
    def __init__(self, session_factory, metrics: MetricsService):
        self.session_factory = session_factory
        self.metrics = metrics

    def emit(self, event: UsageEvent) -> None:
        """
        Receive an event and schedule it for async processing without blocking.
        """
        # We track metrics synchronously
        self.metrics.record_token_consumption(event.total_tokens)

        # Fire and forget the database persistence
        asyncio.create_task(self._process_event(event))

    async def _process_event(self, event: UsageEvent) -> None:
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    # 1. Insert Usage Record
                    record = UsageRecord(
                        organization_id=event.organization_id,
                        workspace_id=event.workspace_id,
                        user_id=event.user_id,
                        api_key_id=event.api_key_id,
                        provider=event.provider,
                        model=event.model,
                        request_tokens=event.request_tokens,
                        response_tokens=event.response_tokens,
                        total_tokens=event.total_tokens,
                        status_code=event.status_code,
                        error_type=event.error_type,
                        is_streaming=event.is_streaming,
                        is_cached=event.is_cached,
                        duration_ms=event.duration_ms,
                    )
                    session.add(record)

                    # 2. Update Quota Windows
                    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

                    scopes = [f"organization:{event.organization_id}"]
                    if event.workspace_id:
                        scopes.append(f"workspace:{event.workspace_id}")
                    if event.api_key_id:
                        scopes.append(f"api_key:{event.api_key_id}")
                    if event.user_id:
                        scopes.append(f"user:{event.user_id}")

                    for scope in scopes:
                        await self._upsert_window(session, scope, "requests", date_str, 1)
                        await self._upsert_window(session, scope, "tokens", date_str, event.total_tokens)
        except Exception as e:
            logger.error(f"Failed to process usage event asynchronously: {e}", exc_info=True)

    async def _upsert_window(
        self, session: AsyncSession, scope_id: str, metric: str, window: str, increment: int
    ) -> None:
        # Generic UPSERT for SQLite/PostgreSQL compatibility
        # For simplicity in this engine we'll attempt select + update, or insert if missing
        from sqlalchemy import select

        stmt = select(QuotaWindow).filter_by(scope_id=scope_id, metric_type=metric, window_id=window).with_for_update()
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            record.value += increment
        else:
            new_record = QuotaWindow(scope_id=scope_id, metric_type=metric, window_id=window, value=increment)
            session.add(new_record)
