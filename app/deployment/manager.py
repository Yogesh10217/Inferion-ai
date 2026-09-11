from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.diagnostics import DeploymentDiagnosticsEngine
from app.deployment.environment import EnvironmentManager
from app.deployment.environment_isolation import EnvironmentIsolationGuard
from app.deployment.health import DeploymentHealthEngine
from app.deployment.liveness import DeploymentLivenessProbe
from app.deployment.models import (
    ConfigurationValidationResult,
    DeploymentEnvironment,
    DeploymentReleaseValidationResult,
    DiagnosticsReport,
    EnvironmentConfig,
    ShutdownState,
    StartupState,
    SystemHealthReport,
)
from app.deployment.readiness import DeploymentReadinessProbe
from app.deployment.release_validation import DeploymentReleaseValidator
from app.deployment.runtime_validation import RuntimeConfigurationValidator
from app.deployment.secrets import EnvironmentSecretProvider, SecretProvider
from app.deployment.shutdown import DeploymentShutdownManager
from app.deployment.startup import DeploymentStartupManager

logger = logging.getLogger("app.deployment.manager")


class DeploymentPlatformManager:
    """Central orchestrator for Phase 5.60 Enterprise AI Production Deployment Foundation."""

    def __init__(
        self,
        container: Optional[ServiceContainer] = None,
        environment_override: Optional[str] = None,
        secret_provider: Optional[SecretProvider] = None,
    ) -> None:
        self.container = container
        self.environment_manager = EnvironmentManager(override_env=environment_override)
        self.config_manager = RuntimeConfigurationManager(self.environment_manager)
        self.secret_provider = secret_provider or EnvironmentSecretProvider()

        self.startup_manager = DeploymentStartupManager(self.config_manager, self.container)
        self.shutdown_manager = DeploymentShutdownManager()

        self.health_engine = DeploymentHealthEngine(self.config_manager, self.container)
        self.diagnostics_engine = DeploymentDiagnosticsEngine(self.config_manager, self.container)
        self.release_validator = DeploymentReleaseValidator(self.config_manager, self.container)

    def get_config(self) -> EnvironmentConfig:
        return self.config_manager.get_config()

    def validate_configuration(self) -> ConfigurationValidationResult:
        config = self.get_config()
        return RuntimeConfigurationValidator.validate(config)

    def startup(self) -> EnvironmentConfig:
        config = self.startup_manager.execute_startup()
        self.shutdown_manager.config = config
        return config

    def shutdown(self) -> ShutdownState:
        return self.shutdown_manager.execute_shutdown()

    def check_health(self) -> SystemHealthReport:
        return self.health_engine.check_health()

    def check_readiness(self) -> Dict[str, Any]:
        if self.startup_manager.state == StartupState.INITIALIZED:
            try:
                self.startup()
            except Exception:
                pass
        probe = DeploymentReadinessProbe(
            config_manager=self.config_manager,
            container=self.container,
            startup_state=self.startup_manager.state,
        )
        return probe.check_readiness()

    def check_liveness(self) -> Dict[str, Any]:
        return DeploymentLivenessProbe.check_liveness()

    def get_diagnostics(self) -> DiagnosticsReport:
        self.diagnostics_engine.startup_state = self.startup_manager.state
        return self.diagnostics_engine.generate_diagnostics()

    def validate_release(self, validation_run: Optional[Any] = None) -> DeploymentReleaseValidationResult:
        return self.release_validator.validate_release_readiness(validation_run=validation_run)


    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.secret_provider.get_secret(key, default)

    def enforce_environment_isolation(self, target_env: DeploymentEnvironment) -> None:
        config = self.get_config()
        EnvironmentIsolationGuard.enforce_environment_match(config, target_env)
