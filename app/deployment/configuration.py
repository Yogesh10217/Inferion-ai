from __future__ import annotations

from typing import Optional

from app.deployment.environment import EnvironmentManager
from app.deployment.models import EnvironmentConfig
from app.deployment.profiles import DeploymentProfile


class RuntimeConfigurationManager:
    """Central configuration manager for application runtime deployment settings."""

    def __init__(self, environment_manager: Optional[EnvironmentManager] = None) -> None:
        self.environment_manager = environment_manager or EnvironmentManager()
        self._config: Optional[EnvironmentConfig] = None
        self._profile: Optional[DeploymentProfile] = None

    def get_config(self) -> EnvironmentConfig:
        if self._config is None:
            self._config = self.environment_manager.load_environment_config()
            self._profile = DeploymentProfile.get_profile(self._config.environment)
        return self._config

    def get_profile(self) -> DeploymentProfile:
        if self._profile is None:
            config = self.get_config()
            self._profile = DeploymentProfile.get_profile(config.environment)
        return self._profile

    def reload(self) -> EnvironmentConfig:
        self._config = self.environment_manager.load_environment_config()
        self._profile = DeploymentProfile.get_profile(self._config.environment)
        return self._config
