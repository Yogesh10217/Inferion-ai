"""Event-Driven Process Orchestration & Event Correlation Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProcessEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"pevt_{uuid.uuid4().hex[:10]}")
    event_type: str
    tenant_id: str = "global"
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:10]}")

    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class EventRouter:
    """Routes incoming process events, deduplicates triggers, and correlates workflow executions."""

    def __init__(self) -> None:
        self._processed_event_ids: List[str] = []

    def dispatch_event(self, event_type: str, payload: Dict[str, Any], tenant_id: str = "global", correlation_id: Optional[str] = None) -> ProcessEvent:
        pevt = ProcessEvent(
            event_type=event_type,
            payload=payload,
            tenant_id=tenant_id,
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:10]}",
        )

        # Deduplication check
        if pevt.event_id in self._processed_event_ids:
            logger.warning(f"[EVENT ROUTER] Duplicate event '{pevt.event_id}' ignored")
            return pevt

        self._processed_event_ids.append(pevt.event_id)
        logger.info(f"[EVENT ROUTER] Dispatched process event '{pevt.event_id}' ({event_type}) for tenant '{tenant_id}' (Correlation: {pevt.correlation_id})")
        return pevt
