from __future__ import annotations

import os
import subprocess  # nosec B404
from typing import Any, Dict

from app.deployment.models import ArtifactIntegrityStatus, DependencyStatus


class DockerPreflightValidator:
    """Performs real preflight checks to determine host Docker daemon and Docker Compose availability."""

    @classmethod
    def check_docker_daemon(cls) -> Dict[str, Any]:
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)  # nosec B603 B607 B404
            if res.returncode == 0:
                return {
                    "available": True,
                    "status": "DOCKER_DAEMON_AVAILABLE",
                    "output": res.stdout[:500],
                    "returncode": 0,
                }
            else:
                return {
                    "available": False,
                    "status": "DOCKER_DAEMON_NOT_AVAILABLE",
                    "output": res.stderr[:500] or res.stdout[:500],
                    "returncode": res.returncode,
                }
        except Exception as e:
            return {
                "available": False,
                "status": "DOCKER_DAEMON_NOT_AVAILABLE",
                "output": str(e),
                "returncode": -1,
            }


class ContainerValidationEngine:
    """Validates Docker container runtime environment, non-root user execution, and manifest integrity."""

    FORBIDDEN_PROD_TAGS = {"latest", "dev", "development", "test", "local", ""}

    @classmethod
    def validate_image_digest(cls, image_digest: str) -> tuple[bool, str]:
        if not image_digest or image_digest.strip() == "" or image_digest == "NOT_AVAILABLE":
            return False, "Image digest is missing or not available"
        raw_digest = image_digest.strip()
        if raw_digest.startswith("@"):
            raw_digest = raw_digest[1:]
        if not raw_digest.startswith("sha256:"):
            return False, "Image digest must use sha256: prefix"
        hex_part = raw_digest.split("sha256:")[-1]
        if len(hex_part) != 64 or not all(c in "0123456789abcdefABCDEF" for c in hex_part):
            return False, "Image digest sha256 hash must contain exactly 64 hexadecimal characters"
        return True, "Image digest format is valid sha256 immutable digest"

    @classmethod
    def validate_runtime_artifact(cls, expected_digest: str, actual_runtime_digest: str) -> tuple[bool, str]:
        digest_valid, msg = cls.validate_image_digest(expected_digest)
        if not digest_valid:
            return False, f"Expected digest invalid: {msg}"
        actual_valid, msg_act = cls.validate_image_digest(actual_runtime_digest)
        if not actual_valid:
            return False, f"Actual runtime digest invalid: {msg_act}"
        exp_clean = expected_digest.strip().lstrip("@")
        act_clean = actual_runtime_digest.strip().lstrip("@")
        if exp_clean.lower() != act_clean.lower():
            return (
                False,
                f"DEPLOYMENT_ARTIFACT_MISMATCH: Expected digest {exp_clean} does not match runtime digest {act_clean}",
            )
        return True, "Runtime artifact digest matches expected deployment identity"

    @classmethod
    def validate_image_tag(cls, image_tag: str, is_production: bool = False) -> tuple[bool, str]:
        if not image_tag or image_tag.strip() == "":
            return False, "Image tag is empty"
        if "@sha256:" in image_tag.lower() or "sha256:" in image_tag.lower():
            valid_dig, msg_dig = cls.validate_image_digest(image_tag.split("@")[-1] if "@" in image_tag else image_tag)
            if valid_dig:
                return True, "Image tag is an immutable sha256 digest reference"
            else:
                return False, f"Invalid image digest reference in tag: {msg_dig}"
        tag_clean = image_tag.split(":")[-1].strip().lower() if ":" in image_tag else image_tag.strip().lower()
        if is_production and (
            tag_clean in cls.FORBIDDEN_PROD_TAGS or image_tag.strip().lower() in cls.FORBIDDEN_PROD_TAGS
        ):
            return False, f"Ambiguous or forbidden image tag '{image_tag}' rejected in PRODUCTION environment"
        return True, "Image tag is production-safe"

    @classmethod
    def validate_container_environment(
        cls, image_tag: str = "enterprise-ai-platform:5.61", is_production: bool = False
    ) -> Dict[str, Any]:
        in_container = os.path.exists("/.dockerenv") or os.getenv("CONTAINERIZED", "false").lower() in ("true", "1")
        user_id = getattr(os, "getuid", lambda: 10001)()
        is_non_root = user_id != 0

        # Check Dockerfile existence
        dockerfile_present = os.path.exists("Dockerfile")
        dockerignore_present = os.path.exists(".dockerignore")

        tag_valid, tag_msg = cls.validate_image_tag(image_tag, is_production=is_production)
        status = (
            DependencyStatus.AVAILABLE
            if (dockerfile_present and dockerignore_present and tag_valid)
            else DependencyStatus.DEGRADED
        )

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
            "artifact_integrity": (
                ArtifactIntegrityStatus.VALID.value if dockerfile_present else ArtifactIntegrityStatus.UNKNOWN.value
            ),
        }
