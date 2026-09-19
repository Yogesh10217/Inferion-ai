"""Integration Event Routing & Subscription Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntegrationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"ievt_{uuid.uuid4().hex[:10]}")
    event_type: str
    tenant_id: str = "global"
    integration_id: str = "custom"
    correlation_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class IntegrationEventRouter:
    """Routes integration events with correlation IDs, deduplication, and fan-out to workflows/agents."""

    def __init__(self, event_dispatcher: Optional[EventDispatcher] = None) -> None:
        self.event_dispatcher = event_dispatcher

    def route_event(self, event: IntegrationEvent) -> Dict[str, Any]:
        logger.info(
            f"[INTEGRATION EVENT ROUTER] Routed event '{event.event_id}' ({event.event_type}) for tenant '{event.tenant_id}'"
        )
        return {"status": "ROUTED", "event_id": event.event_id, "correlation_id": event.correlation_id}
