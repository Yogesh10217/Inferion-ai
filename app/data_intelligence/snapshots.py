"""Immutable data intelligence snapshots (Phase 5.43)."""

from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory


class DataIntelligenceSnapshot(BaseModel):
    snapshot_id: str
    tenant_id: str
    dataset_id: str
    platform_snapshot: PlatformSnapshot
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataIntelligenceSnapshotManager:
    """Creates and retrieves immutable platform snapshots for dataset state & health."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, DataIntelligenceSnapshot] = {}

    def create_snapshot(
        self,
        tenant_id: str,
        dataset_id: str,
        snapshot_payload: Dict[str, Any],
    ) -> DataIntelligenceSnapshot:
        ps = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="DATA_INTELLIGENCE_SNAPSHOT",
            resource_id=dataset_id,
            domain_payload=snapshot_payload,
        )
        sid = ps.metadata.snapshot_id

        dis = DataIntelligenceSnapshot(
            snapshot_id=sid,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            platform_snapshot=ps,
        )
        self._snapshots[sid] = dis
        return dis

    def get_snapshot(self, snapshot_id: str, tenant_id: str) -> DataIntelligenceSnapshot:
        s = self._snapshots.get(snapshot_id)
        if not s:
            raise Exception(f"Snapshot '{snapshot_id}' not found.")
        if s.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return s
