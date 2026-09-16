"""Point-in-time operational state snapshots using PlatformSnapshot and SnapshotFactory primitives."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory


class OperationalAssuranceSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    assurance_score: float
    health_status: str
    reliability_score: float
    platform_snapshot: PlatformSnapshot
    is_finalized: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalAssuranceSnapshotManager:
    """Manages immutable operational assurance snapshots delegating to PlatformSnapshot and SnapshotFactory."""

    def __init__(self, snapshot_factory: Optional[SnapshotFactory] = None) -> None:
        self.snapshot_factory = snapshot_factory or SnapshotFactory()
        self._snapshots: Dict[str, OperationalAssuranceSnapshot] = {}

    def create_snapshot(
        self,
        tenant_id: str,
        service_id: str,
        assurance_score: float = 0.95,
        health_status: str = "EXCELLENT",
        reliability_score: float = 0.95,
        domain_payload: Optional[Dict[str, Any]] = None,
    ) -> OperationalAssuranceSnapshot:
        ps = self.snapshot_factory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="OPERATIONAL_SERVICE",
            resource_id=service_id,
            domain_payload=domain_payload or {
                "assurance_score": assurance_score,
                "health_status": health_status,
                "reliability_score": reliability_score,
            },
        )

        snapshot = OperationalAssuranceSnapshot(
            tenant_id=tenant_id,
            service_id=service_id,
            assurance_score=assurance_score,
            health_status=health_status,
            reliability_score=reliability_score,
            platform_snapshot=ps,
            is_finalized=True,
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> OperationalAssuranceSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap or snap.tenant_id != tenant_id:
            raise CrossTenantOperationsAssuranceException("Access denied.")
        return snap
