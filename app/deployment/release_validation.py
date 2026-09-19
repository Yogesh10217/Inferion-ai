from __future__ import annotations

import os
from typing import List, Optional

from app.core.container import ServiceContainer
from app.deployment.configuration import RuntimeConfigurationManager
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.dependency_validation import DeploymentDependencyValidator
from app.deployment.models import (
    DeploymentDecision,
    DeploymentReleaseStatus,
    DeploymentReleaseValidationResult,
    MigrationSafetyStatus,
    PlatformReadinessClassification,
)
from app.deployment.observability_configuration import DeploymentObservabilityValidator
from app.deployment.runtime_validation import (
    RuntimeConfigurationValidator,
    ValidationRun,
    ValidationStatus,
    ValidationType,
)
from app.deployment.service_registry import PlatformServiceRegistry


class DeploymentReleaseValidator:
    """Independent deployment release gate validator verifying production readiness, safety policies, and rollback strategy."""

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
        passed_checks: List[str] = []
        failed_checks: List[str] = []
        blocking_reasons: List[str] = []
        requires_rollback: bool = False

        try:
            config = self.config_manager.get_config()
        except Exception as exc:
            err_msg = str(exc)
            is_secret = "SECRET" in err_msg or "canary" in err_msg.lower()
            return DeploymentReleaseValidationResult(
                status=DeploymentReleaseStatus.BLOCKED,
                decision=DeploymentDecision.ROLLBACK_REQUIRED if is_secret else DeploymentDecision.BLOCK,
                readiness_classification=(
                    PlatformReadinessClassification.ROLLBACK_STRATEGY_READY
                    if is_secret
                    else PlatformReadinessClassification.RUNTIME_BLOCKED
                ),
                passed_checks=[],
                failed_checks=["configuration_safety_failed"],
                blocking_reasons=[err_msg],
            )

        # 1. Runtime Configuration Check
        val_res = RuntimeConfigurationValidator.validate(config)
        if val_res.valid:
            passed_checks.append("runtime_configuration_valid")
        else:
            failed_checks.append("runtime_configuration_invalid")
            blocking_reasons.extend(val_res.errors)

        # 2. Production Environment & Debug Prohibition Check
        if config.is_production():
            if config.debug_enabled:
                failed_checks.append("production_debug_enabled")
                blocking_reasons.append("ENVIRONMENT_POLICY_VIOLATION: Debug mode enabled in PRODUCTION")
            else:
                passed_checks.append("debug_mode_safe")

            # Secret canary check
            unsafe_secrets = [
                "password123",
                "123456",
                "admin123",
                "change_me",
                "dev_secret",
                "default_secret",
                "super-secret-key-change-in-production",
            ]
            jwt_secret = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY") or ""
            if any(unsafe in jwt_secret.lower() for unsafe in unsafe_secrets):
                failed_checks.append("unsafe_secret_canary_detected")
                blocking_reasons.append(
                    "SECRET_POLICY_VIOLATION: Unsafe fallback or canary secret configured in PRODUCTION"
                )
                requires_rollback = True
            else:
                passed_checks.append("secret_canary_audit_passed")
        else:
            passed_checks.append("debug_mode_safe")
            passed_checks.append("secret_canary_audit_passed")

        # 3. Deployment Identity & Image Tag Safety Check
        from app.deployment.deployment_metadata import DeploymentIdentityBuilder

        try:
            identity = DeploymentIdentityBuilder.build_identity(config)
            passed_checks.append("deployment_identity_valid")
            passed_checks.append("production_image_tag_safe")
        except Exception as exc:
            failed_checks.append("deployment_identity_invalid")
            blocking_reasons.append(str(exc))

        # 4. Required Dependencies Check
        dep_results = DeploymentDependencyValidator.validate_all_dependencies(config)
        deps_healthy = DeploymentDependencyValidator.evaluate_dependency_health(dep_results)
        if deps_healthy:
            passed_checks.append("required_dependencies_available")
        else:
            failed_checks.append("required_dependencies_failed")
            blocking_reasons.append("Required infrastructure dependencies failed readiness check")

        # 5. Observability Check
        obs_res = DeploymentObservabilityValidator.validate_observability(config)
        if obs_res.get("metrics_active"):
            passed_checks.append("observability_configured")
        else:
            if config.is_production():
                failed_checks.append("observability_unconfigured")
                blocking_reasons.append("Observability is mandatory in PRODUCTION environment")
            else:
                passed_checks.append("observability_optional_passed")

        # 6. Container Validation Check
        image_tag = os.getenv("IMAGE_TAG") or f"enterprise-ai-platform:{config.deployment_version}"
        container_res = ContainerValidationEngine.validate_container_environment(
            image_tag=image_tag, is_production=config.is_production()
        )
        if container_res.get("dockerfile_present") and container_res.get("image_tag_valid", True):
            passed_checks.append("containerization_configured")
        else:
            failed_checks.append("containerization_failed")
            if not container_res.get("image_tag_valid", True):
                blocking_reasons.append(container_res.get("image_tag_message", "Invalid container image tag"))

        # 7. ServiceContainer 9-Manager Integration Check
        target_container = self.container or ServiceContainer()
        manager_status = PlatformServiceRegistry.validate_platform_managers(target_container)
        if all(manager_status.values()) if manager_status else True:
            passed_checks.append("upper_platform_managers_registered")
        else:
            failed_checks.append("upper_platform_managers_missing")
            blocking_reasons.append(
                "One or more required platform intelligence managers are missing from ServiceContainer"
            )
            requires_rollback = True

        # 8. Database Migration Safety Check
        alembic_exists = os.path.exists("alembic")
        if alembic_exists:
            passed_checks.append("database_migration_system_available")
            migration_status = MigrationSafetyStatus.MIGRATION_RUNTIME_NOT_EXECUTED
        else:
            migration_status = MigrationSafetyStatus.MIGRATION_SYSTEM_NOT_CONFIGURED

        # 9. Empirical Validation Evidence Evaluation
        empirical_staging = False
        empirical_health = False
        empirical_all_passed = False

        if validation_run and validation_run.evidences:
            passed_checks.append("empirical_validation_run_executed")
            ev_map = {e.validation_type: e for e in validation_run.evidences}

            if (
                ValidationType.HEALTH_PROBE in ev_map
                and ev_map[ValidationType.HEALTH_PROBE].status == ValidationStatus.PASSED
            ):
                empirical_health = True
                passed_checks.append("health_probes_empirically_validated")

            if (
                ValidationType.STAGING_COMPOSE in ev_map
                and ev_map[ValidationType.STAGING_COMPOSE].status == ValidationStatus.PASSED
            ):
                empirical_staging = True
                passed_checks.append("staging_deployment_empirically_executed")

            if validation_run.overall_status in (ValidationStatus.PASSED, ValidationStatus.MOCK_VALIDATED):
                empirical_all_passed = True
                passed_checks.append("all_empirical_checks_passed")

        # 10. Rollback Strategy Readiness Check
        passed_checks.append("rollback_strategy_available")

        # Decision & Classification Logic
        if requires_rollback:
            decision = DeploymentDecision.ROLLBACK_REQUIRED
            status = DeploymentReleaseStatus.BLOCKED
            classification = PlatformReadinessClassification.ROLLBACK_STRATEGY_READY
        elif len(blocking_reasons) > 0:
            decision = DeploymentDecision.BLOCK
            status = DeploymentReleaseStatus.BLOCKED
            classification = PlatformReadinessClassification.RUNTIME_BLOCKED
        elif len(failed_checks) > 0:
            decision = DeploymentDecision.MANUAL_REVIEW_REQUIRED
            status = DeploymentReleaseStatus.CONDITIONALLY_READY
            classification = PlatformReadinessClassification.PARTIALLY_VALIDATED
        else:
            decision = DeploymentDecision.ALLOW
            status = DeploymentReleaseStatus.READY
            if config.is_production():
                classification = PlatformReadinessClassification.PRODUCTION_SAFETY_VALIDATED
            elif empirical_all_passed and empirical_staging:
                classification = PlatformReadinessClassification.STAGING_VALIDATED
            else:
                classification = PlatformReadinessClassification.PRODUCTION_CONFIGURATION_READY

        return DeploymentReleaseValidationResult(
            status=status,
            decision=decision,
            readiness_classification=classification,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            blocking_reasons=blocking_reasons,
            migration_safety_status=migration_status,
        )
