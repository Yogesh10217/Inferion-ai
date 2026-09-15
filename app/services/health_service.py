from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import async_session_maker
from app.providers.provider_factory import ProviderFactory
from app.registry.model_registry import ModelRegistry
from app.services.metrics_service import MetricsService


@dataclass
class ProviderHealth:
    """Strongly typed model representing the health status of a provider."""
    name: str
    status: str  # "healthy" | "unhealthy" | "error"
    message: str | None = None


class HealthService:
    """Service to aggregate system health, readiness, liveness, DB, and Redis information."""

    def __init__(
        self,
        provider_factory: ProviderFactory,
        registry: ModelRegistry,
        metrics_service: MetricsService,
        startup_time: datetime,
        app_version: str,
    ) -> None:
        self.provider_factory = provider_factory
        self.registry = registry
        self.metrics_service = metrics_service
        self.startup_time = startup_time
        self.app_version = app_version

    async def check_database_health(self) -> dict[str, Any]:
        """Check PostgreSQL database connectivity via SELECT 1."""
        try:
            async with async_session_maker() as session:
                res = await session.execute(text("SELECT 1"))
                if res.scalar() == 1:
                    return {"status": "healthy", "message": "Database connection OK"}
                return {"status": "unhealthy", "message": "Unexpected SELECT 1 result"}
        except Exception as exc:
            return {"status": "unhealthy", "message": f"Database error: {exc}"}

    async def check_redis_health(self) -> dict[str, Any]:
        """Check Redis cache and rate-limiting backend connectivity."""
        try:
            settings = get_settings()
            if settings.cache_backend.lower() != "redis" and settings.rate_limit_backend.lower() != "redis":
                return {"status": "disabled", "message": "Redis not configured for cache or rate limiting"}
            
            import redis.asyncio as aioredis
            client = aioredis.from_url(settings.redis_url, socket_timeout=2.0)
            await client.ping()
            await client.aclose()
            return {"status": "healthy", "message": "Redis connection OK"}
        except Exception as exc:
            return {"status": "degraded", "message": f"Redis unreachable: {exc}"}

    async def check_providers_health(self) -> list[ProviderHealth]:
        """Perform health checks on all registered providers."""
        results = []
        for name in self.provider_factory.list_providers():
            try:
                provider = self.provider_factory.get_provider(name)
                is_healthy = await provider.health_check()
                status = "healthy" if is_healthy else "unhealthy"
                results.append(ProviderHealth(name=name, status=status))
            except Exception as e:
                results.append(ProviderHealth(name=name, status="error", message=str(e)))
        return results

    async def get_health_status(self, endpoint: str = "health") -> dict[str, Any]:
        """Compile a full health report of the system including DB and Redis."""
        db_health = await self.check_database_health()
        redis_health = await self.check_redis_health()
        provider_health_list = await self.check_providers_health()

        all_providers_healthy = all(p.status == "healthy" for p in provider_health_list)
        
        if db_health["status"] != "healthy":
            overall_status = "unhealthy"
        elif not all_providers_healthy or redis_health["status"] == "degraded":
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        uptime_seconds = (datetime.now(timezone.utc) - self.startup_time).total_seconds()

        return {
            "status": "ok" if endpoint == "health" else ("ready" if endpoint == "ready" else "alive"),
            "overall_status": overall_status,
            "application_version": self.app_version,
            "uptime": uptime_seconds,
            "startup_timestamp": self.startup_time.isoformat(),
            "database": db_health,
            "redis": redis_health,
            "registered_providers": self.provider_factory.list_providers(),
            "registered_models": [m.id for m in self.registry.list_models()],
            "provider_health": {p.name: p.status for p in provider_health_list},
            "application_state": overall_status,
            "request_count": self.metrics_service.get_request_count(),
        }
