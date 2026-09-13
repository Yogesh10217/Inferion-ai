"""
Tests for Architectural Invariants in Phase 5.70.
"""

from app.core.container import ServiceContainer
from app.deployment.service_registry import PlatformServiceRegistry


def test_single_service_container_and_nine_intelligence_managers():
    container = ServiceContainer()

    # Validate PlatformServiceRegistry returns valid with exactly 9 registered intelligence managers
    registry_validation = PlatformServiceRegistry.validate_platform_managers(container)

    assert len(registry_validation) == 9
    assert all(registry_validation.values())
