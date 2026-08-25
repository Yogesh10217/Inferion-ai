"""Unified Platform Snapshot Metadata Contract (Phase 5.30)."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.fingerprinting import FingerprintGenerator


class SnapshotVersion(BaseModel):
    version: str = "1.0.0"
    schema_version: str = "1.0.0"


class SnapshotMetadata(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_type: str
    resource_id: str
    version: str = "1.0.0"
    contract_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    policy_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fingerprint: str = ""
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class PlatformSnapshot(BaseModel):
    metadata: SnapshotMetadata
    domain_payload: Dict[str, Any] = Field(default_factory=dict)


class SnapshotReference(BaseModel):
    snapshot_id: str
    tenant_id: str
    resource_type: str
    fingerprint: str


class SnapshotFactory:
    """Creates platform snapshots with canonical metadata & fingerprinting."""

    @staticmethod
    def create_snapshot(
        tenant_id: str,
        resource_type: str,
        resource_id: str,
        domain_payload: Dict[str, Any],
        version: str = "1.0.0",
        policy_version: str = "1.0.0",
        contract_version: str = "1.0.0",
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> PlatformSnapshot:
        meta = SnapshotMetadata(
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            version=version,
            contract_version=contract_version,
            policy_version=policy_version,
            extra_metadata=extra_metadata or {},
        )
        fp = FingerprintGenerator.generate({"metadata": meta.model_dump(exclude={"fingerprint"}), "payload": domain_payload}, contract_version)
        meta.fingerprint = fp

        return PlatformSnapshot(metadata=meta, domain_payload=domain_payload)


class SnapshotValidator:
    """Validates snapshot integrity against its fingerprint."""

    @staticmethod
    def validate_snapshot(snapshot: PlatformSnapshot) -> bool:
        meta_dict = snapshot.metadata.model_dump(exclude={"fingerprint"})
        res = FingerprintGenerator.verify(
            {"metadata": meta_dict, "payload": snapshot.domain_payload},
            snapshot.metadata.fingerprint,
            snapshot.metadata.contract_version,
        )
        return res.is_valid
