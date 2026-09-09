"""Capacity snapshot manager for Capacity Intelligence (Phase 5.56)."""

import hashlib
import json
import logging
from app.capacity_intelligence.models import CapacitySnapshot, CapacityAssessment

logger = logging.getLogger(__name__)


class CapacitySnapshotManager:
    """Captures tenant-scoped, timestamped, fingerprint-verified capacity snapshots."""

    def create_snapshot(self, tenant_id: str, assessment: CapacityAssessment) -> CapacitySnapshot:
        raw = json.dumps({"tenant_id": tenant_id, "consumed": assessment.consumed_percentage, "status": assessment.status.value}, sort_keys=True)
        fp = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        snapshot = CapacitySnapshot(
            tenant_id=tenant_id,
            assessment=assessment,
            snapshot_fingerprint=fp,
        )
        logger.info(f"Captured CapacitySnapshot '{snapshot.snapshot_id}' for tenant '{tenant_id}' (Fingerprint: {fp[:12]}...)")
        return snapshot
