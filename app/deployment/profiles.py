from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


@dataclass
class DeploymentProfile:
    environment: DeploymentEnvironment
    allow_debug: bool
    strict_validation: bool
    allow_fallback_secrets: bool
    require_database: bool
    require_cache: bool
    require_messaging: bool
    require_observability: bool
    min_log_level: str

    @classmethod
    def get_profile(cls, env: DeploymentEnvironment) -> DeploymentProfile:
        profiles: Dict[DeploymentEnvironment, DeploymentProfile] = {
            DeploymentEnvironment.LOCAL: cls(
                environment=DeploymentEnvironment.LOCAL,
                allow_debug=True,
                strict_validation=False,
                allow_fallback_secrets=True,
                require_database=False,
                require_cache=False,
                require_messaging=False,
                require_observability=False,
                min_log_level="DEBUG",
            ),
            DeploymentEnvironment.DEVELOPMENT: cls(
                environment=DeploymentEnvironment.DEVELOPMENT,
                allow_debug=True,
                strict_validation=True,
                allow_fallback_secrets=True,
                require_database=False,
                require_cache=False,
                require_messaging=False,
                require_observability=False,
                min_log_level="DEBUG",
            ),
            DeploymentEnvironment.TEST: cls(
                environment=DeploymentEnvironment.TEST,
                allow_debug=True,
                strict_validation=True,
                allow_fallback_secrets=True,
                require_database=False,
                require_cache=False,
                require_messaging=False,
                require_observability=False,
                min_log_level="INFO",
            ),
            DeploymentEnvironment.STAGING: cls(
                environment=DeploymentEnvironment.STAGING,
                allow_debug=False,
                strict_validation=True,
                allow_fallback_secrets=False,
                require_database=True,
                require_cache=False,
                require_messaging=False,
                require_observability=True,
                min_log_level="INFO",
            ),
            DeploymentEnvironment.PRODUCTION: cls(
                environment=DeploymentEnvironment.PRODUCTION,
                allow_debug=False,
                strict_validation=True,
                allow_fallback_secrets=False,
                require_database=True,
                require_cache=True,
                require_messaging=False,
                require_observability=True,
                min_log_level="INFO",
            ),
        }
        return profiles.get(env, profiles[DeploymentEnvironment.LOCAL])

    def validate_config_against_profile(self, config: EnvironmentConfig) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if not self.allow_debug and config.debug_enabled:
            errors.append(f"Debug mode is forbidden in deployment profile '{self.environment.value}'")
        
        if self.strict_validation and not config.application_name:
            errors.append("Application name is required under strict validation profile")
            
        return len(errors) == 0, errors
