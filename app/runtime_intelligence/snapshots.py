"""Runtime snapshot manager for Runtime Intelligence (Phase 5.54)."""

import hashlib
import json
import logging
from app.runtime_intelligence.models import RuntimeSnapshot, RuntimeHealthAssessment

logger = logging.getLogger(__name__)


class RuntimeSnapshotManager:
    """Captures tenant-scoped, timestamped, fingerprint-verified runtime snapshots."""

    def create_snapshot(self, tenant_id: str, health: RuntimeHealthAssessment) -> RuntimeSnapshot:
        raw = json.dumps({"tenant_id": tenant_id, "score": health.overall_score, "status": health.overall_status.value}, sort_keys=True)
        fp = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        snapshot = RuntimeSnapshot(
            tenant_id=tenant_id,
            health=health,
            snapshot_fingerprint=fp,
        )
        logger.info(f"Captured RuntimeSnapshot '{snapshot.snapshot_id}' for tenant '{tenant_id}' (Fingerprint: {fp[:12]}...)")
        return snapshot
