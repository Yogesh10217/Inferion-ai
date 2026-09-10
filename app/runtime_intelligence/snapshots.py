"""Runtime snapshot manager and repository for Runtime Intelligence (Phase 5.57)."""

import hashlib
import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.runtime_intelligence.models import (
    RuntimeSnapshot,
    RuntimeSnapshotMetadata,
    RuntimeHealthAssessment,
    RuntimeHealthStatus,
)
from app.runtime_intelligence.exceptions import (
    CrossTenantRuntimeIntelligenceException,
    ImmutableRuntimeIntelligenceRecordException,
    RuntimeIntelligenceException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class RuntimeSnapshotRepository:
    """Thread-safe, tenant-isolated repository for runtime snapshots."""

    def __init__(self) -> None:
        self._storage: Dict[str, RuntimeSnapshot] = {}
        self._lock = threading.RLock()

    def save(self, snapshot: RuntimeSnapshot) -> None:
        with self._lock:
            existing = self._storage.get(snapshot.snapshot_id)
            if existing and existing.is_finalized:
                raise ImmutableRuntimeIntelligenceRecordException(snapshot.snapshot_id)
            self._storage[snapshot.snapshot_id] = snapshot

    def get_by_id(self, tenant_id: str, snapshot_id: str) -> RuntimeSnapshot:
        with self._lock:
            snap = self._storage.get(snapshot_id)
            if not snap:
                raise RuntimeIntelligenceException("Runtime snapshot not found")
            if snap.tenant_id != tenant_id:
                raise CrossTenantRuntimeIntelligenceException()
            return snap

    def get_by_tenant(self, tenant_id: str) -> List[RuntimeSnapshot]:
        with self._lock:
            return [s for s in self._storage.values() if s.tenant_id == tenant_id]

    def delete(self, tenant_id: str, snapshot_id: str) -> None:
        with self._lock:
            snap = self.get_by_id(tenant_id, snapshot_id)
            if snap.is_finalized:
                raise ImmutableRuntimeIntelligenceRecordException(snapshot_id)
            del self._storage[snapshot_id]


class RuntimeSnapshotManager:
    """Captures, verifies, compares, and finalizes tenant-scoped, SHA-256 sealed runtime snapshots."""

    def __init__(self, repo: Optional[RuntimeSnapshotRepository] = None) -> None:
        self.repo = repo or RuntimeSnapshotRepository()

    def capture_snapshot(
        self,
        tenant_id: str,
        subsystem: str = "global",
        health: Optional[RuntimeHealthAssessment] = None,
        runtime_state: Optional[Dict[str, Any]] = None,
        context_fingerprint: str = "",
        lineage_parent_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> RuntimeSnapshot:
        """Captures a comprehensive runtime snapshot with integrity hashing and lineage."""
        clean_state = SensitiveDataSanitizer.sanitize(runtime_state or {})
        now = datetime.now(timezone.utc)

        if health is None:
            health = RuntimeHealthAssessment(
                tenant_id=tenant_id,
                overall_status=RuntimeHealthStatus.HEALTHY,
                overall_score=1.0,
                dimensions={"availability": 1.0, "latency": 1.0, "error_rate": 1.0},
                subsystem=subsystem,
                evaluated_at=now,
            )

        # Compute deterministic state fingerprint
        state_repr = json.dumps(
            {
                "tenant_id": tenant_id,
                "subsystem": subsystem,
                "health_score": health.overall_score,
                "health_status": health.overall_status.value,
                "context_fingerprint": context_fingerprint,
                "state": clean_state,
            },
            sort_keys=True,
            default=str,
        )
        state_fp = hashlib.sha256(state_repr.encode("utf-8")).hexdigest()

        # Compute full integrity hash
        canonical = json.dumps(
            {
                "tenant_id": tenant_id,
                "subsystem": subsystem,
                "state_fingerprint": state_fp,
                "parent_id": lineage_parent_id,
                "timestamp": now.isoformat(),
            },
            sort_keys=True,
        )
        integrity_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        snapshot_id = f"snap_{integrity_hash[:12]}"

        records_count = len(clean_state.get("signals", [])) if "signals" in clean_state else len(clean_state)
        if records_count == 0:
            records_count = 1

        metadata = RuntimeSnapshotMetadata(
            subsystem=subsystem,
            version="v5.57.0",
            author="RuntimeIntelligenceManager",
            tags=tags or {},
        )

        snapshot = RuntimeSnapshot(
            snapshot_id=snapshot_id,
            tenant_id=tenant_id,
            subsystem=subsystem,
            health=health,
            metadata=metadata,
            runtime_state=clean_state,
            context_fingerprint=context_fingerprint,
            state_fingerprint=state_fp,
            integrity_hash=integrity_hash,
            snapshot_fingerprint=state_fp,
            records_count=records_count,
            is_finalized=True,
            lineage_parent_id=lineage_parent_id,
            captured_at=now,
            created_at=now,
        )

        self.repo.save(snapshot)
        logger.info(
            f"Captured sealed RuntimeSnapshot '{snapshot.snapshot_id}' for tenant '{tenant_id}' (Hash: {integrity_hash[:16]}...)"
        )
        return snapshot

    def create_snapshot(
        self, tenant_id: str, health: RuntimeHealthAssessment, subsystem: str = "global"
    ) -> RuntimeSnapshot:
        """Backwards-compatible convenience creation method."""
        return self.capture_snapshot(tenant_id=tenant_id, subsystem=subsystem, health=health)

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> RuntimeSnapshot:
        return self.repo.get_by_id(tenant_id, snapshot_id)

    def list_snapshots(self, tenant_id: str) -> List[RuntimeSnapshot]:
        return self.repo.get_by_tenant(tenant_id)

    def verify_snapshot(self, tenant_id: str, snapshot_id: str) -> Dict[str, Any]:
        """Verifies snapshot SHA-256 integrity and immutability."""
        snap = self.get_snapshot(tenant_id, snapshot_id)
        state_repr = json.dumps(
            {
                "tenant_id": snap.tenant_id,
                "subsystem": snap.subsystem,
                "health_score": snap.health.overall_score,
                "health_status": snap.health.overall_status.value,
                "context_fingerprint": snap.context_fingerprint,
                "state": snap.runtime_state,
            },
            sort_keys=True,
            default=str,
        )
        recalculated_state_fp = hashlib.sha256(state_repr.encode("utf-8")).hexdigest()
        is_valid = recalculated_state_fp == snap.state_fingerprint
        return {
            "snapshot_id": snapshot_id,
            "tenant_id": tenant_id,
            "is_valid": is_valid,
            "integrity_hash": snap.integrity_hash,
            "is_finalized": snap.is_finalized,
        }

    def compare_snapshots(
        self, tenant_id: str, snapshot_id_1: str, snapshot_id_2: str
    ) -> Dict[str, Any]:
        """Compares two runtime snapshots and detects drift/state differences."""
        s1 = self.get_snapshot(tenant_id, snapshot_id_1)
        s2 = self.get_snapshot(tenant_id, snapshot_id_2)

        health_diff = round(s2.health.overall_score - s1.health.overall_score, 4)
        status_changed = s1.health.overall_status != s2.health.overall_status

        s1_keys = set(s1.runtime_state.keys())
        s2_keys = set(s2.runtime_state.keys())

        return {
            "snapshot_1": s1.snapshot_id,
            "snapshot_2": s2.snapshot_id,
            "tenant_id": tenant_id,
            "health_score_delta": health_diff,
            "status_transition": f"{s1.health.overall_status.value} -> {s2.health.overall_status.value}",
            "status_changed": status_changed,
            "state_fingerprint_match": s1.state_fingerprint == s2.state_fingerprint,
            "added_state_keys": list(s2_keys - s1_keys),
            "removed_state_keys": list(s1_keys - s2_keys),
        }

    def finalize_snapshot(self, tenant_id: str, snapshot_id: str) -> RuntimeSnapshot:
        snap = self.get_snapshot(tenant_id, snapshot_id)
        snap.is_finalized = True
        return snap
