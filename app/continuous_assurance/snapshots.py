"""Snapshot management for Continuous Assurance (Phase 5.54)."""

import logging
from typing import List

from app.continuous_assurance.models import (
    AssuranceDrift,
    ContinuousAssuranceAssessment,
    ContinuousAssuranceSnapshot,
)
from app.continuous_assurance.repositories import SnapshotRepository

logger = logging.getLogger(__name__)


class SnapshotManager:
    """Creates point-in-time state snapshots for continuous assurance evaluation."""

    def __init__(self, snap_repo: SnapshotRepository) -> None:
        self.snap_repo = snap_repo

    def create_snapshot(
        self, tenant_id: str, assessment: ContinuousAssuranceAssessment, drift_events: List[AssuranceDrift]
    ) -> ContinuousAssuranceSnapshot:
        snap = ContinuousAssuranceSnapshot(
            tenant_id=tenant_id,
            assessment=assessment,
            drift_events=drift_events,
        )
        self.snap_repo.save(snap)
        logger.info(f"Created ContinuousAssuranceSnapshot '{snap.snapshot_id}' for tenant '{tenant_id}'")
        return snap
