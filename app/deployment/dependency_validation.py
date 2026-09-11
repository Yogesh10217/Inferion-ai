from __future__ import annotations

from typing import List

from app.deployment.cache_validation import CacheDependencyValidator
from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.database_validation import DatabaseDependencyValidator
from app.deployment.messaging_validation import MessagingDependencyValidator
from app.deployment.models import DependencyCategory, DependencyStatus, DependencyValidationResult, EnvironmentConfig
from app.deployment.observability_configuration import DeploymentObservabilityValidator
from app.deployment.profiles import DeploymentProfile


class DeploymentDependencyValidator:
    """Orchestrates comprehensive dependency validation across database, cache, messaging, and observability."""

    @classmethod
    def validate_all_dependencies(cls, config: EnvironmentConfig) -> List[DependencyValidationResult]:
        results: List[DependencyValidationResult] = []
        profile = DeploymentProfile.get_profile(config.environment)

        # 1. Database
        db_res = DatabaseDependencyValidator.validate_database(
            db_url=config.database_url,
            required=profile.require_database,
        )
        results.append(db_res)

        # 2. Cache
        cache_res = CacheDependencyValidator.validate_cache(
            enabled=config.cache_enabled,
            required=profile.require_cache,
            redis_url=config.redis_url,
        )
        results.append(cache_res)

        # 3. Messaging
        msg_res = MessagingDependencyValidator.validate_messaging(
            enabled=config.messaging_enabled,
            required=profile.require_messaging,
        )
        results.append(msg_res)

        # 4. Observability
        obs_res = DeploymentObservabilityValidator.validate_observability(config)
        obs_status = DependencyStatus(obs_res["status"])
        results.append(
            DependencyValidationResult(
                category=DependencyCategory.OBSERVABILITY,
                name="Prometheus/Observability",
                status=obs_status,
                required=profile.require_observability,
                details=obs_res,
            )
        )

        return results

    @classmethod
    def evaluate_dependency_health(cls, results: List[DependencyValidationResult]) -> bool:
        """Returns True if all REQUIRED dependencies are AVAILABLE or OPTIONAL. Fails if any REQUIRED is UNAVAILABLE."""
        for res in results:
            if res.required and res.status == DependencyStatus.UNAVAILABLE:
                return False
        return True
