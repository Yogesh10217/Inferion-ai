"""Immutable Financial Snapshots (Phase 5.42)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory


class FinOpsSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"snap_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_entity_id: str
    target_entity_type: str  # FINOPS_INVESTIGATION, FINOPS_BUDGET, FINOPS_OPTIMIZATION
    platform_snapshot_id: str
    fingerprint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsSnapshotManager:
    """Manages immutable snapshots for finalized financial entities."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, FinOpsSnapshot] = {}

    def capture_snapshot(
        self,
        tenant_id: str,
        target_entity_id: str,
        target_entity_type: str,
        payload: Dict[str, Any],
    ) -> FinOpsSnapshot:
        plat_snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type=target_entity_type,
            resource_id=target_entity_id,
            domain_payload=payload,
        )
        snap = FinOpsSnapshot(
            tenant_id=tenant_id,
            target_entity_id=target_entity_id,
            target_entity_type=target_entity_type,
            platform_snapshot_id=plat_snap.metadata.snapshot_id,
            fingerprint=plat_snap.metadata.fingerprint,
        )
        self._snapshots[snap.snapshot_id] = snap
        return snap

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> FinOpsSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap or snap.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return snap
