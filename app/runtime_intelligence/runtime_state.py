"""Runtime Operational State Manager for Phase 5.57 Runtime Intelligence."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RuntimeOperationalState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNSTABLE = "UNSTABLE"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"
    RECOVERING = "RECOVERING"
    STABILIZING = "STABILIZING"
    FAILED = "FAILED"


@dataclass
class RuntimeOperationalStateRecord:
    tenant_id: str
    resource_id: str
    state: RuntimeOperationalState
    previous_state: Optional[RuntimeOperationalState] = None
    reason: str = ""
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeStateManager:
    """Tracks and evaluates operational state transitions across monitored runtime resources."""

    def __init__(self) -> None:
        self._states: Dict[str, RuntimeOperationalStateRecord] = {}

    def update_state(
        self, tenant_id: str, resource_id: str, new_state: RuntimeOperationalState, reason: str = ""
    ) -> RuntimeOperationalStateRecord:
        key = f"{tenant_id}:{resource_id}"
        prev_rec = self._states.get(key)
        prev_state = prev_rec.state if prev_rec else None

        rec = RuntimeOperationalStateRecord(
            tenant_id=tenant_id,
            resource_id=resource_id,
            state=new_state,
            previous_state=prev_state,
            reason=reason,
        )
        self._states[key] = rec
        logger.info(f"Runtime operational state for '{key}' updated to {new_state.value} (prev: {prev_state})")
        return rec

    def get_state(self, tenant_id: str, resource_id: str) -> Optional[RuntimeOperationalStateRecord]:
        return self._states.get(f"{tenant_id}:{resource_id}")
