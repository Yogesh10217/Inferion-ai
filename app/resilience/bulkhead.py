"""Bulkhead Isolation Pattern for Resource Pool Protection."""

import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from pydantic import BaseModel

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class BulkheadFullException(AppException):
    """Raised when bulkhead max capacity and queue size are reached."""

    def __init__(self, name: str) -> None:
        super().__init__(
            message=f"Bulkhead pool '{name}' capacity exhausted",
            code="BULKHEAD_FULL",
            status_code=503,
            details={"name": name},
        )


class BulkheadPolicy(BaseModel):
    """Configuration for concurrency limits and queue depth."""

    max_concurrent_calls: int = 10
    max_queued_calls: int = 20


class Bulkhead:
    """Isolates concurrent execution capacity per service/provider/tool component."""

    def __init__(self, name: str, policy: Optional[BulkheadPolicy] = None) -> None:
        self.name = name
        self.policy = policy or BulkheadPolicy()
        self._semaphore = asyncio.Semaphore(self.policy.max_concurrent_calls)
        self._active_calls: int = 0
        self._queued_calls: int = 0

    @property
    def active_calls(self) -> int:
        return self._active_calls

    @property
    def queued_calls(self) -> int:
        return self._queued_calls

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function within bulkhead concurrency and queuing constraints."""
        if self._queued_calls >= self.policy.max_queued_calls:
            logger.warning(f"[BULKHEAD FULL] '{self.name}' queue limit ({self.policy.max_queued_calls}) reached")
            raise BulkheadFullException(self.name)

        self._queued_calls += 1
        try:
            async with self._semaphore:
                self._queued_calls -= 1
                self._active_calls += 1
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                finally:
                    self._active_calls -= 1
        except Exception:
            raise


class BulkheadRegistry:
    """Registry maintaining isolated bulkheads across providers, tools, MCP, agents, and workflows."""

    def __init__(self) -> None:
        self._bulkheads: Dict[str, Bulkhead] = {}

    def get_bulkhead(self, name: str, policy: Optional[BulkheadPolicy] = None) -> Bulkhead:
        if name not in self._bulkheads:
            self._bulkheads[name] = Bulkhead(name, policy or BulkheadPolicy())
        return self._bulkheads[name]

    def list_bulkheads(self) -> Dict[str, Dict[str, int]]:
        return {
            name: {
                "active": bh.active_calls,
                "queued": bh.queued_calls,
            }
            for name, bh in self._bulkheads.items()
        }
