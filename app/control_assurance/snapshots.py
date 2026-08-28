"""Immutable Assurance Snapshots Subsystem (Phase 5.38)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot
from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException


class AssuranceSnapshotMetadata(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"asnap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlAssuranceSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"casnap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    fingerprint_sha256: str
    platform_snapshot_id: str
    state_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlAssuranceSnapshotManager:
    """Manages creation and verification of immutable assurance snapshots."""

    def __init__(
        self,
        snapshot_factory: Optional[SnapshotFactory] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.snapshot_factory = snapshot_factory or SnapshotFactory()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._snapshots: Dict[str, ControlAssuranceSnapshot] = {}

    def create_snapshot(
        self,
        tenant_id: str,
        control_id: str,
        state_payload: Dict[str, Any],
    ) -> ControlAssuranceSnapshot:
        platform_snap = self.snapshot_factory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="CONTROL_ASSURANCE_SNAPSHOT",
            resource_id=control_id,
            domain_payload=state_payload,
        )

        casnap = ControlAssuranceSnapshot(
            tenant_id=tenant_id,
            control_id=control_id,
            fingerprint_sha256=platform_snap.metadata.fingerprint,
            platform_snapshot_id=platform_snap.metadata.snapshot_id,
            state_payload=state_payload,
        )
        self._snapshots[casnap.snapshot_id] = casnap
        return casnap

    def get_snapshot(self, snapshot_id: str, tenant_id: str) -> ControlAssuranceSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            raise CrossTenantControlAssuranceAccessException()
        try:
            self.tenant_guard.enforce_isolation(tenant_id, snap.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()
        return snap
