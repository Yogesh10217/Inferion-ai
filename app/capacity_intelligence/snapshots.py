"""Capacity snapshot manager for Capacity Intelligence (Phase 5.56)."""

import hashlib
import json
import logging
from typing import Optional

from app.capacity_intelligence.models import CapacityAssessment, CapacitySnapshot, CapacityStatus

logger = logging.getLogger(__name__)


class CapacitySnapshotManager:
    """Captures tenant-scoped, timestamped, fingerprint-verified capacity snapshots."""

    def create_snapshot(self, tenant_id: str, assessment: CapacityAssessment) -> CapacitySnapshot:
        raw = json.dumps(
            {"tenant_id": tenant_id, "consumed": assessment.consumed_percentage, "status": assessment.status.value},
            sort_keys=True,
        )
        fp = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        snapshot = CapacitySnapshot(
            tenant_id=tenant_id,
            assessment=assessment,
            snapshot_fingerprint=fp,
        )
        logger.info(
            f"Captured CapacitySnapshot '{snapshot.snapshot_id}' for tenant '{tenant_id}' (Fingerprint: {fp[:12]}...)"
        )
        return snapshot

    def capture_snapshot(self, tenant_id: str, assessment: Optional[CapacityAssessment] = None) -> CapacitySnapshot:
        if assessment is None:
            assessment = CapacityAssessment(
                tenant_id=tenant_id,
                resource_id="res-global",
                consumed_percentage=50.0,
                status=CapacityStatus.HEALTHY,
                headroom_percentage=50.0,
                saturation_risk_score=0.1,
            )
        return self.create_snapshot(tenant_id, assessment)
