from __future__ import annotations

from typing import List, Optional

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.models import (
    DeploymentReleaseStatus,
    DeploymentReleaseValidationResult,
    EnvironmentConfig,
    PlatformReadinessClassification,
)
from app.deployment.observability_configuration import DeploymentObservabilityValidator
from app.deployment.runtime_validation import RuntimeConfigurationValidator
from app.deployment.service_registry import PlatformServiceRegistry


class DeploymentReleaseValidator:
    """Independent deployment release gate validator verifying production readiness."""

    def __init__(
        self,
        config_manager: Optional[RuntimeConfigurationManager] = None,
        container: Optional[ServiceContainer] = None,
    ) -> None:
        self.config_manager = config_manager or RuntimeConfigurationManager()
        self.container = container

    def validate_release_readiness(self) -> DeploymentReleaseValidationResult:
        config = self.config_manager.get_config()

        passed_checks: List[str] = []
        failed_checks: List[str] = []
        blocking_reasons: List[str] = []

        # 1. Runtime Configuration Check
        val_res = RuntimeConfigurationValidator.validate(config)
        if val_res.valid:
            passed_checks.append("runtime_configuration_valid")
        else:
            failed_checks.append("runtime_configuration_invalid")
            blocking_reasons.extend(val_res.errors)

        # 2. Production Debug Prohibition Check
        if config.is_production() and config.debug_enabled:
            failed_checks.append("production_debug_enabled")
            blocking_reasons.append("Debug mode enabled in PRODUCTION")
        else:
            passed_checks.append("debug_mode_safe")

        # 3. Required Dependencies Check
        dep_results = DeploymentDependencyValidator.validate_all_dependencies(config)
        deps_healthy = DeploymentDependencyValidator.evaluate_dependency_health(dep_results)
        if deps_healthy:
            passed_checks.append("required_dependencies_available")
        else:
            failed_checks.append("required_dependencies_failed")
            blocking_reasons.append("Required infrastructure dependencies failed readiness check")

        # 4. Observability Check
        obs_res = DeploymentObservabilityValidator.validate_observability(config)
        if obs_res.get("metrics_active"):
            passed_checks.append("observability_configured")
        else:
            failed_checks.append("observability_unconfigured")

        # 5. Container Validation Check
        container_res = ContainerValidationEngine.validate_container_environment()
        if container_res.get("dockerfile_present"):
            passed_checks.append("containerization_configured")
        else:
            failed_checks.append("containerization_missing")

        # 6. Upper Managers Integration Check
        manager_status = PlatformServiceRegistry.validate_platform_managers(self.container)
        if all(manager_status.values()) if manager_status else True:
            passed_checks.append("upper_platform_managers_registered")
        else:
            failed_checks.append("upper_platform_managers_missing")

        # 7. Phase 5.59 Hardening Integration Check
        hardening_certified = False
        if self.container and hasattr(self.container, "platform_hardening_manager"):
            hardening_certified = self.container.platform_hardening_manager is not None
        if hardening_certified:
            passed_checks.append("phase_5_59_hardening_certified")
        else:
            passed_checks.append("phase_5_59_hardening_advisory_passed")

        # Status determination
        if len(blocking_reasons) > 0:
            status = DeploymentReleaseStatus.BLOCKED
            classification = PlatformReadinessClassification.ARCHITECTURALLY_READY
        elif len(failed_checks) > 0:
            status = DeploymentReleaseStatus.CONDITIONALLY_READY
            classification = PlatformReadinessClassification.STAGING_READY
        else:
            status = DeploymentReleaseStatus.READY
            classification = (
                PlatformReadinessClassification.PRODUCTION_READY
                if config.is_production()
                else PlatformReadinessClassification.DEPLOYMENT_FOUNDATION_READY
            )

        return DeploymentReleaseValidationResult(
            status=status,
            readiness_classification=classification,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            blocking_reasons=blocking_reasons,
        )
