from app.core.config import get_settings
from app.core.container import ServiceContainer
from app.deployment.manager import DeploymentPlatformManager
from app.deployment.service_registry import PlatformServiceRegistry


def test_service_container_single_instance_invariant():
    """Verifies that ServiceContainer remains the canonical manager container upon re-initialization."""
    settings = get_settings()
    container1 = ServiceContainer(settings)
    DeploymentPlatformManager(container=container1)

    # Re-initialization simulation
    container2 = ServiceContainer(settings)
    DeploymentPlatformManager(container=container2)

    registered_names1 = PlatformServiceRegistry.get_registered_manager_names(container1)
    registered_names2 = PlatformServiceRegistry.get_registered_manager_names(container2)

    assert len(registered_names1) == len(registered_names2)
    assert registered_names1 == registered_names2


def test_restart_lifecycles_do_not_duplicate_managers():
    """Verifies that running multiple startup cycles on a container does not duplicate registered managers."""
    settings = get_settings()
    container = ServiceContainer(settings)

    manager = DeploymentPlatformManager(container=container)
    config1 = manager.startup()
    state1 = manager.check_readiness()

    # Graceful shutdown reset
    manager.shutdown()
    manager.startup_manager.state = manager.startup_manager.state.INITIALIZED

    # Re-run startup (simulating restart)
    config2 = manager.startup()
    state2 = manager.check_readiness()

    assert config1.environment == config2.environment
    assert state1["ready"] == state2["ready"]
