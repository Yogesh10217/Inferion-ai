from __future__ import annotations

from app.deployment.exceptions import EnvironmentIsolationError
from app.deployment.models import DeploymentEnvironment, EnvironmentConfig


class EnvironmentIsolationGuard:
    """Enforces strict multi-environment boundaries preventing cross-environment state mutations."""

    @staticmethod
    def enforce_environment_match(
        active_config: EnvironmentConfig,
        target_environment: DeploymentEnvironment,
    ) -> None:
        if active_config.environment != target_environment:
            raise EnvironmentIsolationError(
                f"Access denied: Operation target environment '{target_environment.value}' "
                f"does not match active environment '{active_config.environment.value}'"
            )

    @staticmethod
    def is_operation_permitted(
        active_env: DeploymentEnvironment,
        target_env: DeploymentEnvironment,
    ) -> bool:
        if active_env == target_env:
            return True
        # Local & Dev can share mock probes, but Prod cannot interact with Staging or Dev
        if active_env == DeploymentEnvironment.PRODUCTION and target_env != DeploymentEnvironment.PRODUCTION:
            return False
        return True
