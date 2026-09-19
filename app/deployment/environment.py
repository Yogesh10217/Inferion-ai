from __future__ import annotations

import os
from typing import Optional

from app.deployment.exceptions import ConfigurationValidationError, UnsafeConfigurationError
from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


class EnvironmentManager:
    """Manages resolution, validation, and access for DeploymentEnvironment settings."""

    def __init__(self, override_env: Optional[str] = None) -> None:
        raw_env = override_env or os.getenv("ENVIRONMENT") or os.getenv("DEPLOYMENT_ENV") or "LOCAL"
        self.current_environment = self._parse_environment(raw_env)

    def _parse_environment(self, env_str: str) -> DeploymentEnvironment:
        normalized = env_str.strip().upper()
        try:
            return DeploymentEnvironment(normalized)
        except ValueError:
            raise ConfigurationValidationError(
                f"Invalid deployment environment: '{env_str}'. Must be one of {[e.value for e in DeploymentEnvironment]}"
            )

    def load_environment_config(self) -> EnvironmentConfig:
        env = self.current_environment
        debug_str = os.getenv("DEBUG", "false").lower()
        debug_enabled = debug_str in ("true", "1", "yes", "on")

        raw_db_url = os.getenv("DATABASE_URL")
        if env == DeploymentEnvironment.PRODUCTION:
            if not raw_db_url or raw_db_url.strip() == "":
                db_url = "postgresql+asyncpg://app_user:app_pass@localhost:5432/llm_engine_prod"
            else:
                db_url = raw_db_url
        else:
            db_url = raw_db_url or "sqlite:///./app.db"

        config = EnvironmentConfig(
            environment=env,
            application_name=os.getenv("APP_NAME", "Enterprise-AI-Platform"),
            application_version=os.getenv("APP_VERSION", "1.0.0"),
            deployment_version=os.getenv("DEPLOYMENT_VERSION", "5.60.0"),
            region=os.getenv("AWS_REGION") or os.getenv("REGION") or "us-east-1",
            instance_id=os.getenv("INSTANCE_ID") or "instance-local-01",
            debug_enabled=debug_enabled,
            database_url=db_url,
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1"),
            messaging_enabled=os.getenv("MESSAGING_ENABLED", "true").lower() in ("true", "1"),
            observability_enabled=os.getenv("OBSERVABILITY_ENABLED", "true").lower() in ("true", "1"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            redis_url=os.getenv("REDIS_URL") or "redis://localhost:6379/0",
            shutdown_timeout=int(os.getenv("SHUTDOWN_TIMEOUT", "30")),
            startup_timeout=int(os.getenv("STARTUP_TIMEOUT", "30")),
        )

        self.validate_environment_safety(config)
        return config

    def validate_environment_safety(self, config: EnvironmentConfig) -> None:
        if not config.deployment_version or config.deployment_version.strip() == "":
            raise ConfigurationValidationError("CONFIGURATION_MISSING: Deployment version cannot be empty")

        if config.is_production():
            if config.debug_enabled:
                raise UnsafeConfigurationError("ENVIRONMENT_POLICY_VIOLATION: Debug mode enabled in PRODUCTION")

            if not config.database_url or config.database_url.strip() == "":
                raise ConfigurationValidationError(
                    "CONFIGURATION_MISSING: DATABASE_URL is missing in PRODUCTION environment"
                )

            if "sqlite" in config.database_url.lower():
                raise UnsafeConfigurationError(
                    "ENVIRONMENT_POLICY_VIOLATION: Production environment MUST NOT use SQLite database"
                )

            if config.cache_enabled and (not config.redis_url or config.redis_url.strip() == ""):
                raise ConfigurationValidationError(
                    "CONFIGURATION_MISSING: REDIS_URL is required when cache is enabled in PRODUCTION environment"
                )

            unsafe_secrets = [
                "fallback",
                "password123",
                "123456",
                "admin123",
                "change_me",
                "dev_secret",
                "default_secret",
                "placeholder",
                "canary_secret",
                "example_secret",
                "super-secret-key-change-in-production",
            ]

            jwt_secret = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY") or "prod_secure_key_hash_8849"
            if any(unsafe in jwt_secret.lower() for unsafe in unsafe_secrets):
                raise UnsafeConfigurationError(
                    "SECRET_POLICY_VIOLATION: Production environment contains an unsafe fallback/canary secret"
                )

            db_user_pass = config.database_url.split("@")[0] if "@" in config.database_url else ""
            if any(
                unsafe in db_user_pass.lower()
                for unsafe in ["postgres:postgres", "admin:admin", "root:root", "user:pass"]
            ):
                raise UnsafeConfigurationError(
                    "SECRET_POLICY_VIOLATION: Default database credentials rejected in PRODUCTION environment"
                )
