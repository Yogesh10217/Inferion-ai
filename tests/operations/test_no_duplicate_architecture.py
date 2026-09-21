from app.core.container import ServiceContainer
from app.deployment.service_registry import PlatformServiceRegistry
from app.operations.operations_orchestrator import OperationsOrchestrator


def test_single_service_container_invariant():
    c1 = ServiceContainer()
    assert c1 is not None
    assert hasattr(c1, "inference_service")


def test_exactly_nine_intelligence_managers_registered_in_operations():
    container = ServiceContainer()
    status = PlatformServiceRegistry.validate_platform_managers(container)
    assert len(status) == 9
    assert all(status.values())


def test_operations_orchestrator_is_canonical():
    orchestrator = OperationsOrchestrator()
    assert hasattr(orchestrator, "run_pipeline")
    assert hasattr(orchestrator, "observability_engine")
    assert hasattr(orchestrator, "certification_engine")
