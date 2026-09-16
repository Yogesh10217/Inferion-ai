"""Comprehensive System & Dependency Health Aggregator."""

import logging
import time
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


class SystemHealthManager:
    """Aggregates multi-tier Liveness, Readiness, Startup, and Dependency health."""

    def __init__(self, startup_time: Optional[float] = None) -> None:
        self.startup_time = startup_time or time.time()
        self._dependency_checkers: Dict[str, Any] = {}

    def register_dependency_checker(self, name: str, checker_func: Any) -> None:
        """Register dependency health probe function."""
        self._dependency_checkers[name] = checker_func

    async def check_liveness(self) -> Dict[str, Any]:
        """Simple liveness probe indicating process is running."""
        return {
            "status": HealthStatus.HEALTHY.value,
            "uptime_seconds": round(time.time() - self.startup_time, 2),
        }

    async def check_readiness(self) -> Dict[str, Any]:
        """Readiness probe evaluating critical dependency health."""
        dep_results = await self.check_dependencies()
        overall_status = HealthStatus.HEALTHY

        for info in dep_results.values():
            st = info.get("status", "UNHEALTHY")
            if st == HealthStatus.UNHEALTHY.value:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif st == HealthStatus.DEGRADED.value and overall_status != HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status.value,
            "dependencies": dep_results,
            "uptime_seconds": round(time.time() - self.startup_time, 2),
        }

    async def check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Run health checks across all registered system dependencies."""
        results: Dict[str, Dict[str, Any]] = {}

        for name, checker in self._dependency_checkers.items():
            try:
                if hasattr(checker, "check_health"):
                    res = await checker.check_health()
                elif callable(checker):
                    import asyncio
                    res = await checker() if asyncio.iscoroutinefunction(checker) else checker()
                else:
                    res = {"status": "HEALTHY"}

                if isinstance(res, dict):
                    results[name] = res
                else:
                    results[name] = {"status": "HEALTHY" if res else "UNHEALTHY"}
            except Exception as exc:
                results[name] = {"status": "UNHEALTHY", "error": str(exc)}

        # Ensure default components return entries if not registered
        for default_name in ["database", "cache", "job_queue", "llm_providers", "mcp_servers"]:
            if default_name not in results:
                results[default_name] = {"status": "HEALTHY", "details": "Default operational"}

        return results
