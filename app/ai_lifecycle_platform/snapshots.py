"""Lifecycle Reproducibility Snapshots Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import CrossTenantLifecycleAccessException, ImmutableLifecycleRecordException
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory


class LifecycleSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"lsnap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    snapshot: PlatformSnapshot
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(resource_id=self.snapshot_id, tenant_id=self.tenant_id)


class LifecycleSnapshotManager:
    """Manages lifecycle reproducibility snapshots."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, LifecycleSnapshot] = {}

    def create_snapshot(
        self,
        tenant_id: str,
        asset_id: str,
        domain_payload: Dict[str, Any],
    ) -> LifecycleSnapshot:
        snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="AI_LIFECYCLE_SNAPSHOT",
            resource_id=asset_id,
            domain_payload=domain_payload,
        )
        lsnap = LifecycleSnapshot(tenant_id=tenant_id, asset_id=asset_id, snapshot=snap)
        self._snapshots[lsnap.snapshot_id] = lsnap
        return lsnap

    def finalize_snapshot(self, snapshot_id: str, tenant_id: str) -> LifecycleSnapshot:
        lsnap = self._snapshots.get(snapshot_id)
        if not lsnap:
            raise KeyError(f"Snapshot '{snapshot_id}' not found.")
        if tenant_id != "global" and lsnap.tenant_id != "global" and tenant_id != lsnap.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, lsnap.tenant_id)

        if lsnap.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableLifecycleRecordException(snapshot_id)

        fp = FingerprintGenerator.generate(lsnap.snapshot.model_dump())
        ImmutableResourceValidator.finalize(lsnap.immutable_record, fingerprint=fp)
        return lsnap
