from app.core.container import ServiceContainer
from app.deployment.service_registry import PlatformServiceRegistry


def test_service_container_singleton_and_manager_count_on_restart():
    c1 = ServiceContainer()
    mgrs1 = PlatformServiceRegistry.validate_platform_managers(c1)
    assert len(mgrs1) == 9
    assert all(mgrs1.values()) is True

    # Re-initialize container
    c2 = ServiceContainer()
    mgrs2 = PlatformServiceRegistry.validate_platform_managers(c2)
    assert len(mgrs2) == 9
    assert all(mgrs2.values()) is True
