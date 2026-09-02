"""Immutable Operational Snapshots (Phase 5.41)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory


class OperationalSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"snap_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_entity_id: str
    target_entity_type: str  # OPERATIONAL_INCIDENT, OPERATIONAL_INVESTIGATION, MAJOR_INCIDENT
    platform_snapshot_id: str
    fingerprint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalSnapshotManager:
    """Manages immutable snapshots for finalized operational entities."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, OperationalSnapshot] = {}

    def capture_snapshot(
        self,
        tenant_id: str,
        target_entity_id: str,
        target_entity_type: str,
        payload: Dict[str, Any],
    ) -> OperationalSnapshot:
        plat_snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type=target_entity_type,
            resource_id=target_entity_id,
            domain_payload=payload,
        )
        snap = OperationalSnapshot(
            tenant_id=tenant_id,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type,
            platform_snapshot_id=plat_snap.metadata.snapshot_id,
            fingerprint=plat_snap.metadata.fingerprint,
        )
        self._snapshots[snap.snapshot_id] = snap
        return snap

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> OperationalSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap or snap.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return snap
