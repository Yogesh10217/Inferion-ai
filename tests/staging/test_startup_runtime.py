import pytest
from app.deployment.environment import EnvironmentManager
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.startup import DeploymentStartupManager
from app.deployment.models import DeploymentEnvironment, StartupState
from app.core.container import ServiceContainer
from app.core.config import get_settings


def test_startup_lifecycle_successful():
    """Verifies complete startup lifecycle transition from INITIALIZED to READY."""
    env_mgr = EnvironmentManager(override_env="STAGING")
    cfg_mgr = RuntimeConfigurationManager(env_mgr)
    settings = get_settings()
    container = ServiceContainer(settings)

    startup_mgr = DeploymentStartupManager(cfg_mgr, container)
    assert startup_mgr.state == StartupState.INITIALIZED

    config = startup_mgr.execute_startup()
    assert startup_mgr.state == StartupState.READY
    assert config.environment == DeploymentEnvironment.STAGING


def test_startup_rejected_when_debug_in_production():
    """Verifies that debug mode in PRODUCTION environment causes startup rejection."""
    env_mgr = EnvironmentManager(override_env="PRODUCTION")
    cfg_mgr = RuntimeConfigurationManager(env_mgr)
    config = cfg_mgr.get_config()
    config.debug_enabled = True

    settings = get_settings()
    container = ServiceContainer(settings)
    startup_mgr = DeploymentStartupManager(cfg_mgr, container)

    with pytest.raises(Exception) as exc_info:
        startup_mgr.execute_startup()
    assert startup_mgr.state == StartupState.FAILED
    assert "Debug mode" in str(exc_info.value) or "forbidden" in str(exc_info.value)
