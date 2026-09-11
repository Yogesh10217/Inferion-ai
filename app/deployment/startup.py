from __future__ import annotations

import logging
from typing import Optional

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.exceptions import StartupLifecycleError
from app.deployment.logging_configuration import StructuredLoggingConfigurator
from app.deployment.models import EnvironmentConfig, StartupState
from app.deployment.runtime_validation import RuntimeConfigurationValidator
from app.deployment.service_registry import PlatformServiceRegistry

logger = logging.getLogger("app.deployment.startup")


class DeploymentStartupManager:
    """Orchestrates structured service startup lifecycle transitions and safety validation."""

    VALID_TRANSITIONS = {
        StartupState.INITIALIZED: [StartupState.CONFIGURATION_VALIDATING, StartupState.FAILED],
        StartupState.CONFIGURATION_VALIDATING: [StartupState.DEPENDENCY_VALIDATING, StartupState.FAILED],
        StartupState.DEPENDENCY_VALIDATING: [StartupState.INITIALIZING, StartupState.FAILED],
        StartupState.INITIALIZING: [StartupState.READY, StartupState.FAILED],
        StartupState.READY: [StartupState.FAILED],
        StartupState.FAILED: [],
    }

    def __init__(
        self,
        config_manager: Optional[RuntimeConfigurationManager] = None,
        container: Optional[ServiceContainer] = None,
    ) -> None:
        self.config_manager = config_manager or RuntimeConfigurationManager()
        self.container = container
        self.state = StartupState.INITIALIZED
        self.config: Optional[EnvironmentConfig] = None

    def transition_to(self, new_state: StartupState) -> None:
        allowed = self.VALID_TRANSITIONS.get(self.state, [])
        if new_state not in allowed:
            raise StartupLifecycleError(
                f"Invalid startup state transition: Cannot transition from {self.state.value} to {new_state.value}"
            )
        self.state = new_state

    def execute_startup(self) -> EnvironmentConfig:
        """Executes 11-step startup lifecycle."""
        try:
            # Step 1: Load environment configuration
            self.config = self.config_manager.get_config()

            # Step 2: Validate configuration
            self.transition_to(StartupState.CONFIGURATION_VALIDATING)
            val_res = RuntimeConfigurationValidator.validate(self.config)
            if not val_res.valid:
                error_msg = f"Configuration validation failed: {'; '.join(val_res.errors)}"
                StructuredLoggingConfigurator.log_event(
                    logger, logging.ERROR, "CONFIGURATION_INVALID", error_msg
                )
                self.transition_to(StartupState.FAILED)
                raise StartupLifecycleError(error_msg)

            # Step 3: Validate dependencies
            self.transition_to(StartupState.DEPENDENCY_VALIDATING)
            dep_results = DeploymentDependencyValidator.validate_all_dependencies(self.config)
            dep_healthy = DeploymentDependencyValidator.evaluate_dependency_health(dep_results)
            if not dep_healthy:
                error_msg = "Required infrastructure dependency validation failed"
                StructuredLoggingConfigurator.log_event(
                    logger, logging.ERROR, "DEPENDENCY_UNAVAILABLE", error_msg
                )
                self.transition_to(StartupState.FAILED)
                raise StartupLifecycleError(error_msg)

            # Step 4: Initialize logging
            StructuredLoggingConfigurator.configure_logging(
                environment=self.config.environment.value,
                service=self.config.application_name,
                log_level=self.config.log_level,
            )
            StructuredLoggingConfigurator.log_event(
                logger, logging.INFO, "APPLICATION_STARTING", "Executing application startup lifecycle"
            )

            # Step 5: Initialize observability
            # Step 6: Validate database
            # Step 7: Validate cache
            # Step 8: Validate messaging
            # Step 9: Validate platform container
            self.transition_to(StartupState.INITIALIZING)

            # Step 10: Validate registered managers
            manager_status = PlatformServiceRegistry.validate_platform_managers(self.container)

            # Step 11: Mark application READY
            self.transition_to(StartupState.READY)
            StructuredLoggingConfigurator.log_event(
                logger,
                logging.INFO,
                "APPLICATION_READY",
                f"Application '{self.config.application_name}' is READY in environment '{self.config.environment.value}'",
                extra_data={"registered_managers": manager_status},
            )
            return self.config

        except Exception as exc:
            if self.state != StartupState.FAILED:
                self.state = StartupState.FAILED
            StructuredLoggingConfigurator.log_event(
                logger, logging.CRITICAL, "APPLICATION_FAILED", f"Startup lifecycle failed: {exc}"
            )
            raise
