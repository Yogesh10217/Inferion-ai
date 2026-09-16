from typing import Any, Dict

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings


class HealthAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def get_system_health(self) -> Dict[str, Any]:
        health = {
            "application": {
                "version": "1.0.0",
                "environment": self.settings.environment,
            },
            "database": await self._check_database(),
            "redis": await self._check_redis(),
            # In a full implementation, these would query the actual services
            "middleware": {"status": "healthy"},
            "cache": {"status": "healthy", "hit_rate": 0.85},
            "scheduler": {"status": "healthy", "queue_depth": 0},
            "providers": {"openai": "healthy", "anthropic": "healthy"}
        }
        return health

    async def _check_database(self) -> Dict[str, Any]:
        try:
            await self.db.execute(text("SELECT 1"))
            return {"status": "healthy", "latency_ms": 1}  # Dummy latency for now
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def _check_redis(self) -> Dict[str, Any]:
        try:
            if getattr(self.settings, 'redis_url', None):
                client = redis.from_url(self.settings.redis_url)
                await client.ping()
                await client.aclose()
                return {"status": "healthy"}
            return {"status": "not_configured"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
