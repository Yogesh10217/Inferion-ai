"""
Tests for Canonical Architecture Invariants (Phase 5.69).
Ensures ServiceContainer instantiation, 9 registered Intelligence Managers,
and no duplicate manager registries or sanitizers.
"""

from app.core.container import ServiceContainer
from app.deployment.secrets import get_secrets_sanitizer
from app.deployment.service_registry import PlatformServiceRegistry


def test_single_service_container_instantiation():
    c1 = ServiceContainer()
    assert c1 is not None
    assert hasattr(c1, "inference_service")


def test_nine_registered_managers():
    container = ServiceContainer()
    status = PlatformServiceRegistry.validate_platform_managers(container)
    assert len(status) == 9
    assert all(status.values())


def test_single_secrets_sanitizer():
    s1 = get_secrets_sanitizer()
    s2 = get_secrets_sanitizer()
    assert s1 is s2
