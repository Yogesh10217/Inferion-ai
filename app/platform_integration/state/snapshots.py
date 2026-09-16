"""Platform Integration Snapshot Manager adopting PlatformSnapshot Pattern (Phase 5.58)."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.platform_contracts.snapshots import (
    PlatformSnapshot,
    SnapshotFactory,
)

logger = logging.getLogger(__name__)


@dataclass
class PlatformIntegrationSnapshotRecord:
    snapshot_id: str
    tenant_id: str
    active_platforms: List[str]
    context_fingerprint: str
    overall_assurance_score: float
    state_fingerprint: str
    snapshot: PlatformSnapshot
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PlatformIntegrationSnapshotManager:
    """Captures, fingerprints, and compares point-in-time integration snapshots."""

    def __init__(self) -> None:
        # tenant_id -> list of PlatformIntegrationSnapshotRecord
        self._snapshots: Dict[str, List[PlatformIntegrationSnapshotRecord]] = {}

    def capture_snapshot(
        self,
        tenant_id: str,
        active_platforms: List[str],
        context_fingerprint: str,
        overall_assurance_score: float,
        domain_payload: Optional[Dict[str, Any]] = None,
    ) -> PlatformIntegrationSnapshotRecord:
        snap_id = f"snap-pi-{uuid.uuid4().hex[:12]}"
        payload = domain_payload or {}
        payload.update(
            {
                "active_platforms": active_platforms,
                "context_fingerprint": context_fingerprint,
                "overall_assurance_score": overall_assurance_score,
            }
        )

        canonical_snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="PLATFORM_INTEGRATION_SNAPSHOT",
            resource_id=snap_id,
            domain_payload=payload,
            version="1.0.0",
        )

        record = PlatformIntegrationSnapshotRecord(
            snapshot_id=snap_id,
            tenant_id=tenant_id,
            active_platforms=active_platforms,
            context_fingerprint=context_fingerprint,
            overall_assurance_score=overall_assurance_score,
            state_fingerprint=canonical_snap.metadata.fingerprint,
            snapshot=canonical_snap,
        )

        self._snapshots.setdefault(tenant_id, []).append(record)
        logger.info(f"Captured snapshot {record.snapshot_id} with fingerprint {record.state_fingerprint[:12]}...")
        return record

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> Optional[PlatformIntegrationSnapshotRecord]:
        for s in self._snapshots.get(tenant_id, []):
            if s.snapshot_id == snapshot_id:
                return s
        return None

    def compare_snapshots(
        self,
        snap1: PlatformIntegrationSnapshotRecord,
        snap2: PlatformIntegrationSnapshotRecord,
    ) -> Dict[str, Any]:
        return {
            "snapshot_id_1": snap1.snapshot_id,
            "snapshot_id_2": snap2.snapshot_id,
            "score_delta": round(snap2.overall_assurance_score - snap1.overall_assurance_score, 3),
            "fingerprints_match": snap1.state_fingerprint == snap2.state_fingerprint,
            "platforms_added": list(set(snap2.active_platforms) - set(snap1.active_platforms)),
            "platforms_removed": list(set(snap1.active_platforms) - set(snap2.active_platforms)),
        }
