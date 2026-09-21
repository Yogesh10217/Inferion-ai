from __future__ import annotations

from app.core.container import ServiceContainer
from app.deployment.service_registry import PlatformServiceRegistry


def test_single_service_container_architecture():
    container = ServiceContainer()
    assert container.settings is not None
    assert container.registry is not None
    assert container.health_service is not None


test_manager_list = [
    "lifecycle_manager",
    "evaluation_manager",
    "governance_manager",
    "contract_manager",
    "hardening_manager",
    "readiness_manager",
    "release_validator",
    "environment_manager",
    "deployment_manager",
]


def test_exactly_nine_intelligence_managers():
    container = ServiceContainer()
    manager_status = PlatformServiceRegistry.validate_platform_managers(container)

    assert len(manager_status) == 9
    assert all(manager_status.values())
