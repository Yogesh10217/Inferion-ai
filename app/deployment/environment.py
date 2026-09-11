from __future__ import annotations

import os
from typing import Optional

from app.deployment.exceptions import ConfigurationValidationError, UnsafeConfigurationError
from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


class EnvironmentManager:
    """Manages resolution, validation, and access for DeploymentEnvironment settings."""

    def __init__(self, override_env: Optional[str] = None) -> None:
        raw_env = override_env or os.getenv("DEPLOYMENT_ENV") or os.getenv("ENVIRONMENT") or "LOCAL"
        self.current_environment = self._parse_environment(raw_env)

    def _parse_environment(self, env_str: str) -> DeploymentEnvironment:
        normalized = env_str.strip().upper()
        try:
            return DeploymentEnvironment(normalized)
        except ValueError:
            raise ConfigurationValidationError(f"Invalid deployment environment: '{env_str}'. Must be one of {[e.value for e in DeploymentEnvironment]}")

    def load_environment_config(self) -> EnvironmentConfig:
        env = self.current_environment
        debug_str = os.getenv("DEBUG", "false").lower()
        debug_enabled = debug_str in ("true", "1", "yes", "on")

        db_url = os.getenv("DATABASE_URL") or "sqlite:///./app.db"
        
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
        if config.is_production():
            if config.debug_enabled:
                raise UnsafeConfigurationError("Production environment MUST NOT have debug_enabled=True")
            
            unsafe_secrets = ["fallback", "password123", "123456", "admin123", "change_me", "dev_secret", "default_secret"]
            jwt_secret = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY") or ""
            if any(unsafe in jwt_secret.lower() for unsafe in unsafe_secrets):
                raise UnsafeConfigurationError("Production environment contains an unsafe fallback secret!")

            if "sqlite" in config.database_url.lower():
                # SQLite warning or rejection depending on strict mode
                pass
