from __future__ import annotations

import time
from typing import Optional

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.models import DiagnosticsReport, PlatformReadinessClassification, StartupState
from app.deployment.observability_configuration import DeploymentObservabilityValidator
from app.deployment.runtime_validation import RuntimeConfigurationValidator
from app.deployment.service_registry import PlatformServiceRegistry


class DeploymentDiagnosticsEngine:
    """Assembles comprehensive, sanitized deployment runtime diagnostics."""

    _start_time = time.time()

    def __init__(
        self,
        config_manager: Optional[RuntimeConfigurationManager] = None,
        container: Optional[ServiceContainer] = None,
        startup_state: StartupState = StartupState.READY,
    ) -> None:
        self.config_manager = config_manager or RuntimeConfigurationManager()
        self.container = container
        self.startup_state = startup_state

    def generate_diagnostics(self) -> DiagnosticsReport:
        config = self.config_manager.get_config()
        uptime = time.time() - self._start_time

        val_res = RuntimeConfigurationValidator.validate(config)
        dep_results = DeploymentDependencyValidator.validate_all_dependencies(config)
        registered_managers = PlatformServiceRegistry.get_registered_manager_names(self.container)
        obs_status = DeploymentObservabilityValidator.validate_observability(config)

        # Classification calculation
        if config.is_production() and val_res.valid:
            classification = PlatformReadinessClassification.PRODUCTION_READY
        elif val_res.valid:
            classification = PlatformReadinessClassification.DEPLOYMENT_FOUNDATION_READY
        else:
            classification = PlatformReadinessClassification.ARCHITECTURALLY_READY

        return DiagnosticsReport(
            application_name=config.application_name,
            application_version=config.application_version,
            deployment_version=config.deployment_version,
            environment=config.environment.value,
            startup_state=self.startup_state,
            uptime_seconds=round(uptime, 2),
            registered_managers=registered_managers,
            dependency_health=dep_results,
            configuration_valid=val_res.valid,
            observability_active=obs_status.get("metrics_active", False),
            readiness_classification=classification,
        )
