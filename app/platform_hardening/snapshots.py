"""
Platform Hardening Snapshot Engine.
Captures health, findings, graphs, and readiness diffs for platform audit history.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict

from app.platform_hardening.models import PlatformAuditResult


class PlatformHardeningSnapshotEngine:
    """Captures and compares platform hardening state snapshots."""

    def capture_snapshot(self, audit_result: PlatformAuditResult) -> Dict:
        snapshot_id = f"snap-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        data = {
            "snapshot_id": snapshot_id,
            "tenant_id": audit_result.tenant_id,
            "audit_id": audit_result.audit_id,
            "readiness_score": audit_result.readiness_score,
            "findings_count": len(audit_result.findings),
            "status": audit_result.status.value,
            "captured_at": now.isoformat(),
        }

        payload_str = json.dumps(data, sort_keys=True)
        sha256_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        data["sha256_hash"] = sha256_hash

        return data

    def compute_diff(self, snapshot_a: Dict, snapshot_b: Dict) -> Dict:
        return {
            "readiness_score_diff": snapshot_b.get("readiness_score", 0) - snapshot_a.get("readiness_score", 0),
            "findings_count_diff": snapshot_b.get("findings_count", 0) - snapshot_a.get("findings_count", 0),
        }
