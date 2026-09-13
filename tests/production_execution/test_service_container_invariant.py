import pytest
from app.core.container import ServiceContainer


def test_service_container_initialization_invariant():
    c1 = ServiceContainer()
    assert c1.settings is not None
    assert c1.inference_service is not None
