"""Immutable Model Intelligence Snapshots (Phase 5.44)."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory
from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class ModelIntelligenceSnapshot(BaseModel):
    snapshot_record_id: str
    model_id: str
    tenant_id: str
    platform_snapshot: PlatformSnapshot
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelIntelligenceSnapshotManager:
    """Manages immutable model intelligence snapshots reusing SnapshotFactory."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, ModelIntelligenceSnapshot] = {}

    def capture_snapshot(
        self,
        model_id: str,
        tenant_id: str,
        snapshot_type: str,
        data: Dict[str, Any],
    ) -> ModelIntelligenceSnapshot:
        rec_id = f"msnap-{uuid.uuid4().hex[:8]}"

        psnap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type=f"MODEL_{snapshot_type.upper()}",
            resource_id=model_id,
            domain_payload=data,
        )

        snapshot = ModelIntelligenceSnapshot(
            snapshot_record_id=rec_id,
            model_id=model_id,
            tenant_id=tenant_id,
            platform_snapshot=psnap,
        )

        self._snapshots[rec_id] = snapshot
        logger.info(f"[MODEL SNAPSHOT] Captured snapshot {rec_id} for model {model_id} (Tenant: {tenant_id})")
        return snapshot

    def get_snapshot(self, snapshot_record_id: str, tenant_id: str) -> ModelIntelligenceSnapshot:
        snap = self._snapshots.get(snapshot_record_id)
        if not snap:
            raise ValueError(f"Snapshot record '{snapshot_record_id}' not found.")
        if snap.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return snap
