"""Transaction Manager for ACID boundaries and automatic rollback/retry."""

import asyncio
import logging
from typing import Any, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


class TransactionManager:
    """Manages transactional execution context with automatic rollback and retry protection."""

    def __init__(self, session_factory: Optional[async_sessionmaker[AsyncSession]] = None) -> None:
        self.session_factory = session_factory

    async def execute_in_transaction(
        self,
        func: Callable[[AsyncSession], Any],
        session: Optional[AsyncSession] = None,
        max_retries: int = 3,
    ) -> Any:
        """Execute operation inside a database transaction with retry on concurrency rollback."""
        if session:
            # Join existing active transaction session
            return await self._execute_session(session, func)

        if not self.session_factory:
            # Fallback for mock/non-DB test sessions
            return await func(None)

        attempt = 0
        while attempt < max_retries:
            attempt += 1
            async with self.session_factory() as new_session:
                async with new_session.begin():
                    try:
                        res = await self._execute_session(new_session, func)
                        return res
                    except Exception as exc:
                        logger.warning(f"[TRANSACTION ROLLBACK] Transaction attempt {attempt}/{max_retries} failed: {exc}")
                        if attempt >= max_retries:
                            raise exc
                        await asyncio.sleep(0.1 * (2 ** attempt))

    async def _execute_session(self, session: Optional[AsyncSession], func: Callable) -> Any:
        if asyncio.iscoroutinefunction(func):
            return await func(session)
        return func(session)
