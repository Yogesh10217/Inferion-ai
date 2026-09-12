from __future__ import annotations

import os
from typing import Dict

from app.deployment.exceptions import ConfigurationValidationError
from app.deployment.models import DeploymentEnvironment, DeploymentIdentity, EnvironmentConfig, PlatformReadinessClassification


from app.deployment.container_validation import ContainerValidationEngine


class DeploymentIdentityBuilder:
    """Builds and validates deterministic, sanitized DeploymentIdentity structures."""

    @classmethod
    def build_identity(cls, config: EnvironmentConfig, require_digest: bool = False) -> DeploymentIdentity:
        if not config.deployment_version or config.deployment_version.strip() == "":
            raise ConfigurationValidationError("Deployment version cannot be empty")

        app_version = config.application_version or "1.0.0"
        dep_version = config.deployment_version
        build_id = os.getenv("BUILD_IDENTIFIER") or f"build-{dep_version}"
        git_rev = os.getenv("GIT_REVISION") or os.getenv("COMMIT_SHA") or "head-local"
        image_tag = os.getenv("IMAGE_TAG") or f"enterprise-ai-platform:{dep_version}"
        image_digest = os.getenv("IMAGE_DIGEST") or "NOT_AVAILABLE"

        tag_valid, tag_msg = ContainerValidationEngine.validate_image_tag(image_tag, is_production=config.is_production())
        if not tag_valid:
            raise ConfigurationValidationError(tag_msg)

        if require_digest or (image_digest and image_digest != "NOT_AVAILABLE"):
            dig_valid, dig_msg = ContainerValidationEngine.validate_image_digest(image_digest)
            if not dig_valid:
                raise ConfigurationValidationError(f"Invalid image digest: {dig_msg}")

        return DeploymentIdentity(
            application_version=app_version,
            deployment_version=dep_version,
            build_identifier=build_id,
            git_revision=git_rev,
            environment=config.environment.value,
            image_tag=image_tag,
            image_digest=image_digest,
        )



class DeploymentMetadataProvider:
    """Provides build versioning, git commit hashes, and deployment metadata."""

    @classmethod
    def get_metadata(cls, config: EnvironmentConfig) -> Dict[str, str]:
        identity = DeploymentIdentityBuilder.build_identity(config)
        return {
            "application_name": config.application_name,
            "application_version": identity.application_version,
            "deployment_version": identity.deployment_version,
            "build_identifier": identity.build_identifier,
            "git_revision": identity.git_revision,
            "environment": identity.environment,
            "region": config.region,
            "instance_id": config.instance_id,
            "image_tag": identity.image_tag,
            "image_digest": identity.image_digest,
            "readiness_classification": PlatformReadinessClassification.PRODUCTION_CONFIGURATION_READY.value
            if config.is_production()
            else PlatformReadinessClassification.STAGING_VALIDATED.value,
        }

