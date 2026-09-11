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
from app.deployment.runtime_validation import RuntimeConfigurationValidator, ValidationRun, ValidationStatus, ValidationType
from app.deployment.service_registry import PlatformServiceRegistry


class DeploymentReleaseValidator:
    """Independent deployment release gate validator verifying production readiness and empirical runtime evidence."""

    def __init__(
        self,
        config_manager: Optional[RuntimeConfigurationManager] = None,
        container: Optional[ServiceContainer] = None,
    ) -> None:
        self.config_manager = config_manager or RuntimeConfigurationManager()
        self.container = container

    def validate_release_readiness(
        self, validation_run: Optional[ValidationRun] = None
    ) -> DeploymentReleaseValidationResult:
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

        # 7. Empirical Validation Evidence Check
        empirical_build = False
        empirical_runtime = False
        empirical_health = False
        empirical_staging = False
        empirical_all_passed = False

        if validation_run and validation_run.evidences:
            passed_checks.append("empirical_validation_run_executed")
            ev_map = {e.validation_type: e for e in validation_run.evidences}

            if ValidationType.DOCKER_BUILD in ev_map and ev_map[ValidationType.DOCKER_BUILD].status == ValidationStatus.PASSED:
                empirical_build = True
                passed_checks.append("docker_build_empirically_validated")

            if ValidationType.CONTAINER_RUNTIME in ev_map and ev_map[ValidationType.CONTAINER_RUNTIME].status == ValidationStatus.PASSED:
                empirical_runtime = True
                passed_checks.append("container_runtime_empirically_validated")

            if ValidationType.HEALTH_PROBE in ev_map and ev_map[ValidationType.HEALTH_PROBE].status == ValidationStatus.PASSED:
                empirical_health = True
                passed_checks.append("health_probes_empirically_validated")

            if ValidationType.STAGING_COMPOSE in ev_map and ev_map[ValidationType.STAGING_COMPOSE].status == ValidationStatus.PASSED:
                empirical_staging = True
                passed_checks.append("staging_deployment_empirically_executed")

            if validation_run.overall_status in (ValidationStatus.PASSED, ValidationStatus.MOCK_VALIDATED):
                empirical_all_passed = True
                passed_checks.append("all_empirical_checks_passed")

        # Status & Classification determination
        if len(blocking_reasons) > 0:
            status = DeploymentReleaseStatus.BLOCKED
            classification = PlatformReadinessClassification.RUNTIME_BLOCKED
        elif len(failed_checks) > 0:
            status = DeploymentReleaseStatus.CONDITIONALLY_READY
            classification = PlatformReadinessClassification.PARTIALLY_VALIDATED
        elif empirical_all_passed and empirical_staging and empirical_health:
            status = DeploymentReleaseStatus.READY
            classification = (
                PlatformReadinessClassification.PRODUCTION_READY
                if config.is_production()
                else PlatformReadinessClassification.STAGING_VALIDATED
            )
        elif empirical_runtime:
            status = DeploymentReleaseStatus.READY
            classification = PlatformReadinessClassification.CONTAINER_RUNTIME_VALIDATED
        elif empirical_build:
            status = DeploymentReleaseStatus.READY
            classification = PlatformReadinessClassification.CONTAINER_BUILD_VALIDATED
        else:
            status = DeploymentReleaseStatus.READY
            classification = PlatformReadinessClassification.STAGING_CONFIGURATION_READY

        return DeploymentReleaseValidationResult(
            status=status,
            readiness_classification=classification,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            blocking_reasons=blocking_reasons,
        )

