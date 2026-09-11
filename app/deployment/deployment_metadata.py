from __future__ import annotations

import os

from app.deployment.models import EnvironmentConfig, PlatformReadinessClassification


class DeploymentMetadataProvider:
    """Provides build versioning, git commit hashes, and deployment metadata."""

    @classmethod
    def get_metadata(cls, config: EnvironmentConfig) -> dict[str, str]:
        return {
            "application_name": config.application_name,
            "application_version": config.application_version,
            "deployment_version": config.deployment_version,
            "environment": config.environment.value,
            "region": config.region,
            "instance_id": config.instance_id,
            "build_hash": os.getenv("BUILD_HASH", "sha256-5.60.0-release"),
            "readiness_classification": PlatformReadinessClassification.DEPLOYMENT_FOUNDATION_READY.value,
        }
