"""Security Assurance Snapshot Manager."""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.snapshots import SnapshotFactory
from app.security_assurance.exceptions import CrossTenantSecurityAssuranceException

logger = logging.getLogger(__name__)


class SecurityAssuranceSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"sec-snap-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    posture_score: float
    threats_count: int
    vulnerabilities_count: int
    incidents_count: int
    sha256_hash: str
    is_finalized: bool = True
    idempotency_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityAssuranceSnapshotManager:
    """Manages creation, immutability, and indexing of point-in-time security posture snapshots."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, SecurityAssuranceSnapshot] = {}
        self._idempotency_map: Dict[str, str] = {}
        self.snapshot_factory = SnapshotFactory()

    def create_snapshot(
        self,
        tenant_id: str,
        posture_score: float,
        threats_count: int,
        vulnerabilities_count: int,
        incidents_count: int,
        idempotency_key: Optional[str] = None,
    ) -> SecurityAssuranceSnapshot:
        if idempotency_key and idempotency_key in self._idempotency_map:
            existing_id = self._idempotency_map[idempotency_key]
            return self.get_snapshot(tenant_id, existing_id)

        data = {
            "tenant_id": tenant_id,
            "posture_score": posture_score,
            "threats_count": threats_count,
            "vulnerabilities_count": vulnerabilities_count,
            "incidents_count": incidents_count,
        }
        sha256_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

        snapshot = SecurityAssuranceSnapshot(
            tenant_id=tenant_id,
            posture_score=posture_score,
            threats_count=threats_count,
            vulnerabilities_count=vulnerabilities_count,
            incidents_count=incidents_count,
            sha256_hash=sha256_hash,
            is_finalized=True,
            idempotency_key=idempotency_key,
        )

        self._snapshots[snapshot.snapshot_id] = snapshot
        if idempotency_key:
            self._idempotency_map[idempotency_key] = snapshot.snapshot_id

        logger.info(
            f"[SECURITY SNAPSHOT] Created immutable security snapshot {snapshot.snapshot_id} (SHA-256: {sha256_hash[:8]}...)"
        )
        return snapshot

    def get_snapshot(self, tenant_id: str, snapshot_id: str) -> SecurityAssuranceSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            raise KeyError(f"Snapshot '{snapshot_id}' not found.")
        if snap.tenant_id != tenant_id:
            raise CrossTenantSecurityAssuranceException(
                f"Tenant '{tenant_id}' cannot access snapshot for tenant '{snap.tenant_id}'."
            )
        return snap

    def list_snapshots(self, tenant_id: str) -> List[SecurityAssuranceSnapshot]:
        return [s for s in self._snapshots.values() if s.tenant_id == tenant_id]
