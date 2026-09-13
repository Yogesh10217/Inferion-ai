import pytest
from app.core.container import ServiceContainer
from app.deployment.service_registry import PlatformServiceRegistry


def test_single_service_container_architecture_invariant():
    container = ServiceContainer()
    assert container.settings is not None
    assert container.registry is not None
    assert container.health_service is not None
    mgrs = PlatformServiceRegistry.get_registered_manager_names(container)
    assert len(mgrs) == 9
