from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.deployment.container_validation import ContainerValidationEngine
from app.deployment.models import DeploymentEnvironment, DeploymentIdentity


@dataclass
class ProductionReleaseManifest:
    """Immutable release candidate manifest separating stable identity from volatile metadata."""

    application_version: str
    deployment_version: str
    build_identifier: str
    git_revision: str
    environment: str
    image_reference: str
    image_tag: str
    image_digest: str = "NOT_AVAILABLE"
    configuration_fingerprint: str = ""
    build_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    release_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def stable_identity_payload(self) -> Dict[str, Any]:
        """Returns stable identity fields without volatile timestamps."""
        return {
            "application_version": self.application_version,
            "deployment_version": self.deployment_version,
            "build_identifier": self.build_identifier,
            "git_revision": self.git_revision,
            "environment": self.environment,
            "image_reference": self.image_reference,
            "image_tag": self.image_tag,
            "image_digest": self.image_digest,
            "configuration_fingerprint": self.configuration_fingerprint,
        }

    def canonical_fingerprint(self) -> str:
        """Deterministic fingerprint calculated strictly over stable identity data."""
        payload = self.stable_identity_payload()
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def validate_manifest(self) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        is_prod = self.environment == DeploymentEnvironment.PRODUCTION.value

        # 1. Version presence
        if not self.application_version or not self.application_version.strip():
            errors.append("MANIFEST_ERROR: Missing application_version")
        if not self.deployment_version or not self.deployment_version.strip():
            errors.append("MANIFEST_ERROR: Missing deployment_version")

        # 2. Git revision presence
        if not self.git_revision or not self.git_revision.strip():
            errors.append("MANIFEST_ERROR: Missing git_revision")

        # 3. Forbidden image tag checks
        tag_valid, tag_msg = ContainerValidationEngine.validate_image_tag(self.image_tag, is_production=is_prod)
        if not tag_valid:
            errors.append(f"MANIFEST_ERROR: {tag_msg}")

        # 4. Image digest validation if present
        if self.image_digest and self.image_digest != "NOT_AVAILABLE":
            dig_valid, dig_msg = ContainerValidationEngine.validate_image_digest(self.image_digest)
            if not dig_valid:
                errors.append(f"MANIFEST_ERROR: {dig_msg}")

        return len(errors) == 0, errors

    @classmethod
    def create_from_identity(
        cls,
        identity: DeploymentIdentity,
        configuration_fingerprint: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProductionReleaseManifest:
        img_ref = (
            f"{identity.image_tag}@{identity.image_digest}"
            if identity.image_digest != "NOT_AVAILABLE"
            else identity.image_tag
        )
        return cls(
            application_version=identity.application_version,
            deployment_version=identity.deployment_version,
            build_identifier=identity.build_identifier,
            git_revision=identity.git_revision,
            environment=identity.environment,
            image_reference=img_ref,
            image_tag=identity.image_tag,
            image_digest=identity.image_digest,
            configuration_fingerprint=configuration_fingerprint,
            metadata=metadata or {},
        )
