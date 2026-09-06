"""Immutable decision snapshots reusing PlatformSnapshot and SnapshotFactory primitives."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotFactory
from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException


class DecisionSnapshotStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class DecisionGovernanceSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    decision_id: str
    snapshot_ref: PlatformSnapshot
    status: DecisionSnapshotStatus = DecisionSnapshotStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionSnapshotManager:
    """Manages snapshot generation for decision governance states."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, DecisionGovernanceSnapshot] = {}

    def capture_snapshot(
        self,
        tenant_id: str,
        decision_id: str,
        state_data: Dict[str, Any],
    ) -> DecisionGovernanceSnapshot:
        p_snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            snapshot_type="DECISION_GOVERNANCE_SNAPSHOT",
            state_data={"decision_id": decision_id, **state_data},
            metadata={"source": "DecisionSnapshotManager"},
        )

        snap = DecisionGovernanceSnapshot(
            tenant_id=tenant_id,
            decision_id=decision_id,
            snapshot_ref=p_snap,
        )
        self._snapshots[snap.snapshot_id] = snap
        return snap

    def get_snapshot(self, snapshot_id: str, tenant_id: str) -> DecisionGovernanceSnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            raise ValueError(f"Snapshot '{snapshot_id}' not found")
        if snap.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return snap
