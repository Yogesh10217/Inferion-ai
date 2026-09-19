"""
Checkpoint Manager for State Snapshots & Failure Recovery
"""

import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.autonomy.exceptions import CheckpointError

logger = logging.getLogger(__name__)


class ExecutionSnapshot(BaseModel):
    checkpoint_id: str
    execution_id: str
    tenant_id: str = "default_tenant"
    step_number: int
    state_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class CheckpointManager:
    """Manages incremental execution snapshots and rollback state recovery."""

    def __init__(self):
        self._checkpoints: Dict[str, List[ExecutionSnapshot]] = {}

    def save_checkpoint(
        self, execution_id: str, step_number: int, state_data: Dict[str, Any], tenant_id: str = "default_tenant"
    ) -> ExecutionSnapshot:
        cid = f"chk_{execution_id}_{step_number}_{int(time.time() * 1000)}"
        snapshot = ExecutionSnapshot(
            checkpoint_id=cid,
            execution_id=execution_id,
            tenant_id=tenant_id,
            step_number=step_number,
            state_data=state_data,
        )
        if execution_id not in self._checkpoints:
            self._checkpoints[execution_id] = []
        self._checkpoints[execution_id].append(snapshot)
        logger.info(f"[CHECKPOINT] Saved checkpoint '{cid}' for execution '{execution_id}' at step {step_number}")
        return snapshot

    def get_latest_checkpoint(self, execution_id: str) -> Optional[ExecutionSnapshot]:
        snapshots = self._checkpoints.get(execution_id, [])
        return snapshots[-1] if snapshots else None

    def rollback_to_checkpoint(self, execution_id: str, step_number: int) -> ExecutionSnapshot:
        snapshots = self._checkpoints.get(execution_id, [])
        for snap in reversed(snapshots):
            if snap.step_number <= step_number:
                logger.info(
                    f"[CHECKPOINT] Rolled back execution '{execution_id}' to step {snap.step_number} (chk: {snap.checkpoint_id})"
                )
                return snap
        raise CheckpointError(f"No checkpoint found for execution '{execution_id}' at step <= {step_number}")
