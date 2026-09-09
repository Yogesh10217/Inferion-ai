"""Runtime Execution Tracking Engine for Phase 5.57 Runtime Intelligence."""

import logging
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DelegationExecutionState(str, Enum):
    REQUESTED = "REQUESTED"
    DISPATCHED = "DISPATCHED"
    ACCEPTED = "ACCEPTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass
class DelegationExecutionRecord:
    tenant_id: str
    delegation_id: str
    action_type: str
    state: DelegationExecutionState
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeExecutionTracker:
    """Observes and tracks post-delegation execution state without executing external mutations directly."""

    def __init__(self) -> None:
        self._tracking_records: Dict[str, DelegationExecutionRecord] = {}

    def track_delegation(
        self, tenant_id: str, delegation_id: str, action_type: str, state: DelegationExecutionState = DelegationExecutionState.REQUESTED
    ) -> DelegationExecutionRecord:
        rec = DelegationExecutionRecord(
            tenant_id=tenant_id,
            delegation_id=delegation_id,
            action_type=action_type,
            state=state,
        )
        self._tracking_records[delegation_id] = rec
        logger.info(f"Tracking delegation '{delegation_id}' ({action_type}): state={state.value}")
        return rec

    def get_delegation_state(self, delegation_id: str) -> Optional[DelegationExecutionRecord]:
        return self._tracking_records.get(delegation_id)
