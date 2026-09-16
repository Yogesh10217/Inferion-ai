"""
Autonomous Workflow Snapshot Subsystem.
Captures point-in-time workflow state snapshots for auditability and historic playback.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.autonomous_assurance.exceptions import CrossTenantAutonomousAssuranceException
from app.platform_contracts.snapshots import SnapshotFactory


class AutonomousWorkflowSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"wfsnap_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    status: str
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    evidence_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutonomousSnapshotStore:
    """Stores point-in-time workflow snapshots."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, List[AutonomousWorkflowSnapshot]] = {}
        self.factory = SnapshotFactory()

    def capture_snapshot(
        self,
        workflow_id: str,
        tenant_id: str,
        status: str,
        state_snapshot: Optional[Dict[str, Any]] = None,
        evidence_hash: Optional[str] = None,
    ) -> AutonomousWorkflowSnapshot:
        snap = AutonomousWorkflowSnapshot(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            status=status,
            state_snapshot=state_snapshot or {},
            evidence_hash=evidence_hash,
        )
        if workflow_id not in self._snapshots:
            self._snapshots[workflow_id] = []
        self._snapshots[workflow_id].append(snap)
        return snap

    def list_snapshots(self, workflow_id: str, tenant_id: str) -> List[AutonomousWorkflowSnapshot]:
        snaps = self._snapshots.get(workflow_id, [])
        for s in snaps:
            if s.tenant_id != tenant_id and tenant_id != "global":
                raise CrossTenantAutonomousAssuranceException(f"Unauthorized access to snapshots for workflow '{workflow_id}'")
        return snaps
