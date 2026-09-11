from typing import Dict, Any, Optional

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.models import StartupState
from app.deployment.runtime_validation import RuntimeConfigurationValidator
from app.deployment.service_registry import PlatformServiceRegistry


class DeploymentReadinessProbe:
    """Evaluates whether application is READY to handle live production traffic."""

    def __init__(
        self,
        config_manager: Optional[RuntimeConfigurationManager] = None,
        container: Optional[ServiceContainer] = None,
        startup_state: StartupState = StartupState.READY,
    ) -> None:
        self.config_manager = config_manager or RuntimeConfigurationManager()
        self.container = container
        self.startup_state = startup_state

    def check_readiness(self) -> Dict[str, Any]:
        config = self.config_manager.get_config()

        # 1. Config validation
        val_res = RuntimeConfigurationValidator.validate(config)
        config_ok = val_res.valid

        # 2. Dependency validation
        dep_results = DeploymentDependencyValidator.validate_all_dependencies(config)
        deps_ok = DeploymentDependencyValidator.evaluate_dependency_health(dep_results)

        # 3. Manager validation
        managers_ok = len(PlatformServiceRegistry.get_registered_manager_names(self.container)) > 0 if self.container else True

        # 4. Startup state check
        startup_ok = self.startup_state in (StartupState.READY, StartupState.INITIALIZED)

        is_ready = config_ok and deps_ok and managers_ok and startup_ok
        effective_startup_state = StartupState.READY if is_ready else self.startup_state

        return {
            "status": "READY" if is_ready else "NOT_READY",
            "ready": is_ready,
            "environment": config.environment.value,
            "checks": {
                "configuration_valid": config_ok,
                "dependencies_available": deps_ok,
                "managers_registered": managers_ok,
                "startup_state": effective_startup_state.value,
            },
        }
