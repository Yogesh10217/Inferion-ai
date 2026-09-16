"""Recovery and Resilience Snapshots Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.snapshots import SnapshotFactory
from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException, ResilienceResourceNotFoundException


class ResilienceSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"ressnap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    snapshot_type: str = "RESILIENCE_STATE"
    fingerprint_sha256: str = ""
    platform_snapshot_id: Optional[str] = None
    state_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceSnapshotManager:
    """Resilience Snapshot Manager leveraging SnapshotFactory."""

    def __init__(
        self,
        snapshot_factory: Optional[SnapshotFactory] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.snapshot_factory = snapshot_factory or SnapshotFactory()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._snapshots: Dict[str, ResilienceSnapshot] = {}

    def create_snapshot(
        self,
        tenant_id: str,
        resource_id: str,
        state_payload: Dict[str, Any],
    ) -> ResilienceSnapshot:
        platform_snap = self.snapshot_factory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="RESILIENCE_SNAPSHOT",
            resource_id=resource_id,
            domain_payload=state_payload,
        )

        res_snap = ResilienceSnapshot(
            tenant_id=tenant_id,
            resource_id=resource_id,
            fingerprint_sha256=platform_snap.metadata.fingerprint,
            platform_snapshot_id=platform_snap.metadata.snapshot_id,
            state_payload=state_payload,
        )
        self._snapshots[res_snap.snapshot_id] = res_snap
        return res_snap

    def get_snapshot(self, snapshot_id: str, tenant_id: str) -> ResilienceSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            raise ResilienceResourceNotFoundException(snapshot_id)

        try:
            self.tenant_guard.enforce_isolation(tenant_id, snap.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, snap.tenant_id)

        return snap
