from __future__ import annotations

import re
from typing import List

from app.deployment.configuration_fingerprint import ConfigurationFingerprintEngine
from app.deployment.models import ConfigurationValidationResult, EnvironmentConfig
from app.deployment.profiles import DeploymentProfile


class RuntimeConfigurationValidator:
    """Validates runtime deployment configuration constraints and safety invariants."""

    URL_REGEX = re.compile(r"^(https?|postgresql|mysql|sqlite|redis|amqp)(\+[a-z0-9_]+)?://", re.IGNORECASE)

    @classmethod
    def validate(cls, config: EnvironmentConfig) -> ConfigurationValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        profile = DeploymentProfile.get_profile(config.environment)

        # Profile validation
        valid_profile, profile_errors = profile.validate_config_against_profile(config)
        if not valid_profile:
            errors.extend(profile_errors)

        # Production safety checks
        if config.is_production():
            if config.debug_enabled:
                errors.append("CRITICAL: Debug mode is explicitly forbidden in PRODUCTION environment")
            if not config.observability_enabled:
                warnings.append("WARNING: Observability is recommended to be enabled in PRODUCTION")
            if "sqlite" in config.database_url.lower():
                warnings.append("WARNING: SQLite database used in PRODUCTION profile; PostgreSQL recommended")

        # URL format checks
        if config.database_url and not cls.URL_REGEX.match(config.database_url):
            errors.append(f"Invalid database_url format: '{config.database_url}'")

        # Service ID and version validation
        if not config.application_name or not config.application_name.strip():
            errors.append("Application name must not be empty")

        if not config.deployment_version or not config.deployment_version.strip():
            errors.append("Deployment version must not be empty")

        # Generate fingerprint
        fp = ConfigurationFingerprintEngine.generate_fingerprint(config)

        return ConfigurationValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            configuration_fingerprint=fp.fingerprint_hash,
        )
