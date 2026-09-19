"""Access Snapshot Governance (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException
from app.platform_contracts.snapshots import SnapshotFactory


class AccessSnapshot(BaseModel):
    """Access Intelligence Snapshot Representation."""

    snapshot_id: str = Field(default_factory=lambda: f"snap_acc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_entity_id: str
    target_entity_type: str  # ACCESS_INVESTIGATION, ACCESS_REVIEW, ACCESS_CERTIFICATION, ACCESS_GOVERNANCE
    platform_snapshot_id: str
    fingerprint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessSnapshotManager:
    """Manages immutable snapshots for finalized access governance states."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, AccessSnapshot] = {}

    def capture_snapshot(
        self,
        tenant_id: str,
        target_entity_id: str,
        target_entity_type: str,
        state_payload: Dict[str, Any],
    ) -> AccessSnapshot:
        plat_snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type=target_entity_type,
            resource_id=target_entity_id,
            domain_payload=state_payload,
        )
        snap = AccessSnapshot(
            tenant_id=tenant_id,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type,
            platform_snapshot_id=plat_snap.metadata.snapshot_id,
            fingerprint=plat_snap.metadata.fingerprint,
        )
        self._snapshots[snap.snapshot_id] = snap
        return snap

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> AccessSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap or snap.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return snap

    def list_snapshots(self, tenant_id: str) -> List[AccessSnapshot]:
        return [s for s in self._snapshots.values() if s.tenant_id == tenant_id]
