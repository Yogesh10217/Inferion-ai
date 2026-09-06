"""Identity Assurance Snapshots."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException
from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot


class IdentityAssuranceSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    assurance_score: float
    trust_score: float
    risk_level: str
    platform_snapshot: PlatformSnapshot
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityAssuranceSnapshotManager:
    """Manages identity assurance snapshots delegating to PlatformSnapshot and SnapshotFactory."""

    def __init__(self, snapshot_factory: Optional[SnapshotFactory] = None) -> None:
        self.snapshot_factory = snapshot_factory or SnapshotFactory()
        self._snapshots: Dict[str, IdentityAssuranceSnapshot] = {}

    def create_snapshot(
        self,
        tenant_id: str,
        identity_id: str,
        assurance_score: float = 0.90,
        trust_score: float = 0.95,
        risk_level: str = "LOW",
        domain_payload: Optional[Dict[str, Any]] = None,
    ) -> IdentityAssuranceSnapshot:
        ps = self.snapshot_factory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="IDENTITY",
            resource_id=identity_id,
            domain_payload=domain_payload or {
                "assurance_score": assurance_score,
                "trust_score": trust_score,
                "risk_level": risk_level,
            },
        )

        snapshot = IdentityAssuranceSnapshot(
            tenant_id=tenant_id,
            identity_id=identity_id,
            assurance_score=assurance_score,
            trust_score=trust_score,
            risk_level=risk_level,
            platform_snapshot=ps,
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> IdentityAssuranceSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap or snap.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return snap
