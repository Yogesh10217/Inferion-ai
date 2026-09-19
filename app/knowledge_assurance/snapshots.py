"""Knowledge Assurance Snapshots Module.

Provides point-in-time state snapshots using PlatformSnapshot and SnapshotFactory primitives.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeReferenceNotFoundException,
)
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory


class KnowledgeSnapshotStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    PURGED = "PURGED"


class KnowledgeAssuranceSnapshot(BaseModel):
    assurance_snapshot_id: str = Field(default_factory=lambda: f"kasnap-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    target_resource_id: str
    snapshot_type: str = "KNOWLEDGE_ASSURANCE"
    platform_snapshot_id: str
    status: KnowledgeSnapshotStatus = KnowledgeSnapshotStatus.ACTIVE
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeAssuranceSnapshotManager:
    """Manages knowledge assurance snapshots."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, KnowledgeAssuranceSnapshot] = {}

    def create_snapshot(
        self,
        tenant_id: str,
        target_resource_id: str,
        snapshot_type: str = "KNOWLEDGE_ASSURANCE",
        state_data: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeAssuranceSnapshot:
        psnap: PlatformSnapshot = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type=snapshot_type,
            resource_id=target_resource_id,
            domain_payload=state_data or {"target_resource_id": target_resource_id},
        )

        kasnap = KnowledgeAssuranceSnapshot(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            snapshot_type=snapshot_type,
            platform_snapshot_id=psnap.snapshot_id,
            metadata={"checksum": psnap.checksum},
        )
        self._snapshots[kasnap.assurance_snapshot_id] = kasnap
        return kasnap

    def get_snapshot(self, tenant_id: str, assurance_snapshot_id: str) -> KnowledgeAssuranceSnapshot:
        if assurance_snapshot_id not in self._snapshots:
            raise KnowledgeReferenceNotFoundException(f"Snapshot {assurance_snapshot_id} not found.")
        snap = self._snapshots[assurance_snapshot_id]
        if snap.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return snap

    def list_snapshots(
        self, tenant_id: str, target_resource_id: Optional[str] = None
    ) -> List[KnowledgeAssuranceSnapshot]:
        results = [s for s in self._snapshots.values() if s.tenant_id == tenant_id]
        if target_resource_id:
            results = [s for s in results if s.target_resource_id == target_resource_id]
        return results
