from app.core.container import ServiceContainer
from app.deployment.service_registry import PlatformServiceRegistry


def test_exactly_nine_intelligence_managers_registered():
    container = ServiceContainer()
    status = PlatformServiceRegistry.validate_platform_managers(container)

    assert len(status) == 9
    assert all(status.values())
