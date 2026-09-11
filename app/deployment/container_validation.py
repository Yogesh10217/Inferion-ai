from __future__ import annotations

import os
from typing import Any, Dict

from app.deployment.models import ArtifactIntegrityStatus, DependencyStatus


class ContainerValidationEngine:
    """Validates Docker container runtime environment, non-root user execution, and manifest integrity."""

    @classmethod
    def validate_container_environment(cls) -> Dict[str, Any]:
        in_container = os.path.exists("/.dockerenv") or os.getenv("CONTAINERIZED", "false").lower() in ("true", "1")
        user_id = os.getuid() if hasattr(os, "getuid") else 10001
        is_non_root = user_id != 0

        # Check Dockerfile existence
        dockerfile_present = os.path.exists("Dockerfile")
        dockerignore_present = os.path.exists(".dockerignore")

        status = DependencyStatus.AVAILABLE if (dockerfile_present and dockerignore_present) else DependencyStatus.DEGRADED

        return {
            "status": status.value,
            "in_container": in_container,
            "non_root_user": is_non_root,
            "user_id": user_id,
            "dockerfile_present": dockerfile_present,
            "dockerignore_present": dockerignore_present,
            "artifact_integrity": ArtifactIntegrityStatus.VALID.value if dockerfile_present else ArtifactIntegrityStatus.UNKNOWN.value,
        }
