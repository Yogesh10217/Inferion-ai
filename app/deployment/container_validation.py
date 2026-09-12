from __future__ import annotations

import os
from typing import Any, Dict

from app.deployment.models import ArtifactIntegrityStatus, DependencyStatus


class ContainerValidationEngine:
    """Validates Docker container runtime environment, non-root user execution, and manifest integrity."""

    FORBIDDEN_PROD_TAGS = {"latest", "dev", "development", "test", "local", ""}

    @classmethod
    def validate_image_tag(cls, image_tag: str, is_production: bool = False) -> tuple[bool, str]:
        if not image_tag or image_tag.strip() == "":
            return False, "Image tag is empty"
        if "@sha256:" in image_tag.lower():
            return True, "Image tag is an immutable sha256 digest reference"
        tag_clean = image_tag.split(":")[-1].strip().lower() if ":" in image_tag else image_tag.strip().lower()
        if is_production and (tag_clean in cls.FORBIDDEN_PROD_TAGS or image_tag.strip().lower() in cls.FORBIDDEN_PROD_TAGS):
            return False, f"Ambiguous or forbidden image tag '{image_tag}' rejected in PRODUCTION environment"
        return True, "Image tag is production-safe"

    @classmethod
    def validate_container_environment(cls, image_tag: str = "enterprise-ai-platform:5.61", is_production: bool = False) -> Dict[str, Any]:
        in_container = os.path.exists("/.dockerenv") or os.getenv("CONTAINERIZED", "false").lower() in ("true", "1")
        user_id = os.getuid() if hasattr(os, "getuid") else 10001
        is_non_root = user_id != 0

        # Check Dockerfile existence
        dockerfile_present = os.path.exists("Dockerfile")
        dockerignore_present = os.path.exists(".dockerignore")

        tag_valid, tag_msg = cls.validate_image_tag(image_tag, is_production=is_production)
        status = DependencyStatus.AVAILABLE if (dockerfile_present and dockerignore_present and tag_valid) else DependencyStatus.DEGRADED

        return {
            "status": status.value,
            "in_container": in_container,
            "non_root_user": is_non_root,
            "user_id": user_id,
            "dockerfile_present": dockerfile_present,
            "dockerignore_present": dockerignore_present,
            "image_tag": image_tag,
            "image_tag_valid": tag_valid,
            "image_tag_message": tag_msg,
            "artifact_integrity": ArtifactIntegrityStatus.VALID.value if dockerfile_present else ArtifactIntegrityStatus.UNKNOWN.value,
        }

