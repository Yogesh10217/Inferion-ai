from __future__ import annotations

from typing import List, Optional

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.models import (
    DependencyStatus,
    HealthCategory,
    HealthCheckResult,
    HealthStatus,
    SystemHealthReport,
)
from app.deployment.service_registry import PlatformServiceRegistry


class DeploymentHealthEngine:
    """Aggregates system-wide operational health probes into sanitized health reports."""

    def __init__(
        self,
        config_manager: Optional[RuntimeConfigurationManager] = None,
        container: Optional[ServiceContainer] = None,
    ) -> None:
        self.config_manager = config_manager or RuntimeConfigurationManager()
        self.container = container

    def check_health(self) -> SystemHealthReport:
        config = self.config_manager.get_config()
        checks: List[HealthCheckResult] = []

        # 1. Application check
        checks.append(
            HealthCheckResult(
                category=HealthCategory.APPLICATION,
                name="ApplicationRuntime",
                status=HealthStatus.HEALTHY,
                details={"name": config.application_name, "version": config.application_version},
            )
        )

        # 2. Dependency checks
        dep_results = DeploymentDependencyValidator.validate_all_dependencies(config)
        for dep in dep_results:
            health_stat = HealthStatus.HEALTHY
            if dep.status == DependencyStatus.DEGRADED:
                health_stat = HealthStatus.DEGRADED
            elif dep.status == DependencyStatus.UNAVAILABLE:
                health_stat = HealthStatus.UNHEALTHY if dep.required else HealthStatus.DEGRADED

            cat_map = {
                "DATABASE": HealthCategory.DATABASE,
                "CACHE": HealthCategory.CACHE,
                "MESSAGE_BROKER": HealthCategory.MESSAGING,
                "OBSERVABILITY": HealthCategory.OBSERVABILITY,
            }
            health_cat = cat_map.get(dep.category.name, HealthCategory.APPLICATION)

            checks.append(
                HealthCheckResult(
                    category=health_cat,
                    name=dep.name,
                    status=health_stat,
                    details={"latency_ms": dep.latency_ms, "required": dep.required},
                )
            )

        # 3. Platform Container check
        container_res = ContainerValidationEngine.validate_container_environment()
        checks.append(
            HealthCheckResult(
                category=HealthCategory.PLATFORM_CONTAINER,
                name="DockerContainer",
                status=HealthStatus.HEALTHY if container_res["status"] == "AVAILABLE" else HealthStatus.DEGRADED,
                details=container_res,
            )
        )

        # 4. Intelligence Managers check
        manager_status = PlatformServiceRegistry.validate_platform_managers(self.container)
        all_managers_ready = all(manager_status.values()) if manager_status else True
        checks.append(
            HealthCheckResult(
                category=HealthCategory.INTELLIGENCE_MANAGERS,
                name="PlatformManagers",
                status=HealthStatus.HEALTHY if all_managers_ready else HealthStatus.DEGRADED,
                details={
                    "registered_count": sum(1 for v in manager_status.values() if v),
                    "total": len(manager_status),
                },
            )
        )

        # Overall Status Determination
        overall_status = HealthStatus.HEALTHY
        for c in checks:
            if c.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif c.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED

        return SystemHealthReport(
            status=overall_status,
            environment=config.environment.value,
            version=config.application_version,
            checks=checks,
        )
