"""Application Configuration & Environment Management (Phase 5.22 - Component 4).

Supports environments: DEVELOPMENT, TESTING, STAGING, PRODUCTION.
Secret references are resolved through SecretManager (never plaintext).
HIGH or CRITICAL production config changes require ApprovalEngine authorization.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

from app.approvals.approval_engine import ApprovalEngine
from app.application_platform.exceptions import ApplicationPlatformException

logger = logging.getLogger(__name__)


class ApplicationEnvironment(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class EnvironmentConfiguration(BaseModel):
    """Environment-specific override configuration."""

    env_config_id: str = Field(default_factory=lambda: f"envcfg_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    environment: ApplicationEnvironment = ApplicationEnvironment.DEVELOPMENT
    feature_overrides: Dict[str, Any] = Field(default_factory=dict)
    model_overrides: Dict[str, str] = Field(default_factory=dict)
    prompt_overrides: Dict[str, str] = Field(default_factory=dict)
    secret_references: Dict[str, str] = Field(default_factory=dict)
    runtime_limits: Dict[str, Any] = Field(default_factory=dict)
    updated_by: str = "system"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConfigurationVersion(BaseModel):
    """Versioned snapshot of environment configuration."""

    config_version_id: str = Field(default_factory=lambda: f"cfgver_{uuid.uuid4().hex[:12]}")
    environment_config: EnvironmentConfiguration
    version_number: int = 1
    approval_request_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConfigurationManager:
    """Manages environment configurations, secret resolutions, and change risk gating."""

    def __init__(
        self,
        secret_manager: Optional[SecretManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self.approval_engine = approval_engine or ApprovalEngine()
        self._env_configs: Dict[str, EnvironmentConfiguration] = {}  # key: f"{tenant_id}:{app_id}:{env}"

    def set_environment_config(
        self,
        tenant_id: str,
        application_id: str,
        environment: ApplicationEnvironment,
        feature_overrides: Optional[Dict[str, Any]] = None,
        model_overrides: Optional[Dict[str, str]] = None,
        prompt_overrides: Optional[Dict[str, str]] = None,
        secret_references: Optional[Dict[str, str]] = None,
        runtime_limits: Optional[Dict[str, Any]] = None,
        risk_level: str = "LOW",
        updated_by: str = "system",
    ) -> EnvironmentConfiguration:
        key = f"{tenant_id}:{application_id}:{environment.value}"
        
        cfg = EnvironmentConfiguration(
            application_id=application_id,
            tenant_id=tenant_id,
            environment=environment,
            feature_overrides=feature_overrides or {},
            model_overrides=model_overrides or {},
            prompt_overrides=prompt_overrides or {},
            secret_references=secret_references or {},
            runtime_limits=runtime_limits or {},
            updated_by=updated_by,
        )

        # Gate HIGH / CRITICAL risk production configuration updates via ApprovalEngine
        if environment == ApplicationEnvironment.PRODUCTION and risk_level.upper() in {"HIGH", "CRITICAL"}:
            req = self.approval_engine.create_approval_request(
                requester=updated_by,
                action=f"Update PRODUCTION configuration for app '{application_id}'",
                context={
                    "tenant_id": tenant_id,
                    "application_id": application_id,
                    "environment": environment.value,
                    "risk_level": risk_level,
                },
            )
            logger.info(f"[CONFIG MANAGER] HIGH/CRITICAL config update requires approval request {req.request_id}")
            cfg.metadata["approval_request_id"] = req.request_id

        self._env_configs[key] = cfg
        return cfg

    def get_environment_config(
        self,
        tenant_id: str,
        application_id: str,
        environment: ApplicationEnvironment,
    ) -> EnvironmentConfiguration:
        key = f"{tenant_id}:{application_id}:{environment.value}"
        if key not in self._env_configs:
            # Default empty configuration
            return EnvironmentConfiguration(
                application_id=application_id,
                tenant_id=tenant_id,
                environment=environment,
            )
        return self._env_configs[key]

    def resolve_secret(self, secret_reference: str) -> Optional[str]:
        """Safely resolve secret value through SecretManager without storing plaintext."""
        try:
            return self.secret_manager.get_secret(secret_reference)
        except Exception as e:
            logger.error(f"[CONFIG MANAGER] Failed to resolve secret reference '{secret_reference}': {e}")
            return None
