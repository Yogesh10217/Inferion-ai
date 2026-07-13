from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

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
    """Service to aggregate system health, readiness, and liveness information."""

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
        """Compile a full health report of the system."""
        provider_health_list = await self.check_providers_health()
        
        # Check overall status: if any provider has an error or is unhealthy, overall might be degraded,
        # but the app itself might still be considered healthy. Let's make overall_status depend on providers.
        # If all providers are healthy, overall is healthy.
        all_healthy = all(p.status == "healthy" for p in provider_health_list)
        overall_status = "healthy" if all_healthy else "degraded"

        uptime_seconds = (datetime.now(timezone.utc) - self.startup_time).total_seconds()

        # Build response map
        return {
            "status": "ok" if endpoint == "health" else ("ready" if endpoint == "ready" else "alive"),
            "overall_status": overall_status,
            "application_version": self.app_version,
            "uptime": uptime_seconds,
            "startup_timestamp": self.startup_time.isoformat(),
            "registered_providers": self.provider_factory.list_providers(),
            "registered_models": [m.id for m in self.registry.list_models()],
            "provider_health": {p.name: p.status for p in provider_health_list},
            "application_state": "healthy",
            "request_count": self.metrics_service.get_request_count(),
            "memory_usage": "0 MB",  # Placeholder
        }
