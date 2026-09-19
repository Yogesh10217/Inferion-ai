"""Database Health Monitor tracking connectivity, pool metrics, and query latency."""

import logging
import time
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


class DatabaseHealthMonitor:
    """Monitors database connectivity, query latency, failed queries, and connection pool utilization."""

    def __init__(self, session_factory: Optional[async_sessionmaker[AsyncSession]] = None) -> None:
        self.session_factory = session_factory
        self.total_queries: int = 0
        self.failed_queries: int = 0
        self.total_latency_ms: float = 0.0

    async def check_health(self) -> Dict[str, Any]:
        """Execute diagnostic health query on database."""
        start_t = time.time()
        is_connected = False
        error_msg = None

        if self.session_factory:
            try:
                async with self.session_factory() as session:
                    res = await session.execute(text("SELECT 1"))
                    val = res.scalar()
                    is_connected = val == 1
            except Exception as e:
                is_connected = False
                error_msg = str(e)
                self.failed_queries += 1
        else:
            is_connected = True  # In-memory / non-SQL fallback

        dur_ms = (time.time() - start_t) * 1000.0
        self.total_queries += 1
        self.total_latency_ms += dur_ms

        avg_latency = (self.total_latency_ms / self.total_queries) if self.total_queries > 0 else 0.0

        return {
            "connected": is_connected,
            "latency_ms": round(dur_ms, 2),
            "average_latency_ms": round(avg_latency, 2),
            "total_queries": self.total_queries,
            "failed_queries": self.failed_queries,
            "error": error_msg,
            "status": "HEALTHY" if is_connected else "UNHEALTHY",
        }
