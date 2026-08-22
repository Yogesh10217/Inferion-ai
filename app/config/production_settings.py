"""Production Configuration Validation & Feature Flags System."""

import os
import logging
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.security.exceptions import SecurityPolicyViolation

logger = logging.getLogger(__name__)


class EnvironmentName(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class FeatureFlags(BaseModel):
    """Runtime feature toggles across platform capabilities."""

    enable_circuit_breaker: bool = True
    enable_rate_limiting: bool = True
    enable_quotas: bool = True
    enable_job_queue: bool = True
    enable_distributed_lock: bool = True
    enable_audit_logging: bool = True
    enable_observability: bool = True
    enable_auto_failover: bool = True
    enable_streaming: bool = True


class ProductionSettings(BaseModel):
    """Strict configuration settings for production deployments."""

    environment: EnvironmentName = EnvironmentName.DEVELOPMENT
    jwt_secret: str = "super-secret-key-change-in-production"
    database_url: str = "sqlite+aiosqlite:///./data/engine.db"
    redis_url: Optional[str] = "redis://localhost:6379"
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])
    min_worker_threads: int = 4
    max_worker_threads: int = 32
    enable_ssl: bool = False
    feature_flags: FeatureFlags = Field(default_factory=FeatureFlags)


class ConfigurationValidator:
    """Validates configuration parameters and fails fast on unsafe production settings."""

    @staticmethod
    def validate_production_configuration(settings: ProductionSettings) -> Dict[str, Any]:
        """Perform security audit on runtime configuration."""
        env = settings.environment
        errors: List[str] = []
        warnings: List[str] = []

        if env == EnvironmentName.PRODUCTION:
            # 1. Unsafe JWT Secret
            if settings.jwt_secret in ("super-secret-key-change-in-production", "change-me", "secret", "123456"):
                errors.append("PRODUCTION SECURITY ERROR: Default or weak 'jwt_secret' configured in production environment!")

            # 2. SQLite in Production Warning
            if "sqlite" in settings.database_url.lower():
                warnings.append("PRODUCTION WARNING: SQLite database configured for production environment. PostgreSQL is recommended.")

            # 3. Open CORS / Hosts
            if "*" in settings.allowed_hosts:
                warnings.append("PRODUCTION WARNING: Wildcard '*' in allowed_hosts!")

            # 4. Redis backend check
            if not settings.redis_url:
                warnings.append("PRODUCTION WARNING: No Redis URL configured. Distributed caching/locks will default to in-memory.")

        if errors:
            err_msg = "; ".join(errors)
            logger.critical(f"[CONFIG VALIDATION FAILED] {err_msg}")
            raise SecurityPolicyViolation(err_msg)

        if warnings:
            for w in warnings:
                logger.warning(f"[CONFIG VALIDATION WARNING] {w}")

        return {
            "valid": True,
            "environment": env.value,
            "errors": errors,
            "warnings": warnings,
        }
