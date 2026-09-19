"""
Decision Snapshots Subsystem.
Captures immutable point-in-time state snapshots of decisions for auditability and historic playback.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import CrossTenantDecisionIntelligenceException


class DecisionPointInTimeSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    state: str
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)
    scoring_snapshot: Dict[str, Any] = Field(default_factory=dict)
    reproducibility_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionSnapshotStore:
    """Stores immutable point-in-time snapshots for decisions."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, List[DecisionPointInTimeSnapshot]] = {}

    def capture_snapshot(
        self,
        decision_id: str,
        tenant_id: str,
        state: str,
        context_snapshot: Optional[Dict[str, Any]] = None,
        scoring_snapshot: Optional[Dict[str, Any]] = None,
        reproducibility_hash: Optional[str] = None,
    ) -> DecisionPointInTimeSnapshot:
        snap = DecisionPointInTimeSnapshot(
            decision_id=decision_id,
            tenant_id=tenant_id,
            state=state,
            context_snapshot=context_snapshot or {},
            scoring_snapshot=scoring_snapshot or {},
            reproducibility_hash=reproducibility_hash,
        )
        if decision_id not in self._snapshots:
            self._snapshots[decision_id] = []
        self._snapshots[decision_id].append(snap)
        return snap

    def list_snapshots(self, decision_id: str, tenant_id: str) -> List[DecisionPointInTimeSnapshot]:
        snaps = self._snapshots.get(decision_id, [])
        for snap in snaps:
            if snap.tenant_id != tenant_id and tenant_id != "global":
                raise CrossTenantDecisionIntelligenceException(
                    f"Unauthorized access to snapshots for decision '{decision_id}'"
                )
        return snaps
