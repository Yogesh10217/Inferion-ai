"""Artifact Integrity & References Subsystem (Phase 5.33)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.ai_lifecycle_platform.exceptions import ArtifactIntegrityException, CrossTenantLifecycleAccessException


class ArtifactType(str, Enum):
    MODEL_BINARY = "MODEL_BINARY"
    CONFIGURATION = "CONFIGURATION"
    PROMPT_TEMPLATE = "PROMPT_TEMPLATE"
    AGENT_CONFIGURATION = "AGENT_CONFIGURATION"
    EVALUATION_RESULT = "EVALUATION_RESULT"
    DATASET_MANIFEST = "DATASET_MANIFEST"
    DEPLOYMENT_MANIFEST = "DEPLOYMENT_MANIFEST"


class ArtifactStatus(str, Enum):
    REGISTERED = "REGISTERED"
    VERIFIED = "VERIFIED"
    CORRUPTED = "CORRUPTED"
    DEPRECATED = "DEPRECATED"


class ArtifactIntegrity(BaseModel):
    is_valid: bool = True
    fingerprint: str = ""


class ArtifactReference(BaseModel):
    uri: str
    size_bytes: int = 1024


class AIArtifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"art_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    artifact_type: ArtifactType = ArtifactType.MODEL_BINARY
    status: ArtifactStatus = ArtifactStatus.REGISTERED
    reference: ArtifactReference = Field(default_factory=lambda: ArtifactReference(uri="s3://artifacts/binary.bin"))
    sha256_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArtifactManager:
    """Manages artifact references and verifies SHA-256 integrity."""

    def __init__(self) -> None:
        self._artifacts: Dict[str, AIArtifact] = {}

    def register_artifact(
        self,
        tenant_id: str,
        name: str,
        artifact_type: ArtifactType = ArtifactType.MODEL_BINARY,
        uri: str = "s3://artifacts/binary.bin",
        content_payload: Optional[Dict[str, Any]] = None,
    ) -> AIArtifact:
        fp = FingerprintGenerator.generate(content_payload or {"name": name, "uri": uri})
        art = AIArtifact(
            tenant_id=tenant_id,
            name=name,
            artifact_type=artifact_type,
            reference=ArtifactReference(uri=uri),
            sha256_hash=fp,
            status=ArtifactStatus.VERIFIED,
        )
        self._artifacts[art.artifact_id] = art
        return art

    def verify_integrity(self, artifact_id: str, tenant_id: str, current_payload: Dict[str, Any]) -> ArtifactIntegrity:
        art = self.get_artifact(artifact_id, tenant_id)
        current_fp = FingerprintGenerator.generate(current_payload)
        if current_fp != art.sha256_hash:
            raise ArtifactIntegrityException(artifact_id, art.sha256_hash, current_fp)
        return ArtifactIntegrity(is_valid=True, fingerprint=art.sha256_hash)

    def get_artifact(self, artifact_id: str, tenant_id: str) -> AIArtifact:
        art = self._artifacts.get(artifact_id)
        if not art:
            raise KeyError(f"Artifact '{artifact_id}' not found.")
        if tenant_id != "global" and art.tenant_id != "global" and tenant_id != art.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, art.tenant_id)
        return art
