"""
Event Engine for Autonomous Execution & Reactive Workflows
"""

import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AutonomyEventType(str, Enum):
    TOOL_COMPLETED = "TOOL_COMPLETED"
    TOOL_FAILED = "TOOL_FAILED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    MEMORY_UPDATED = "MEMORY_UPDATED"
    KNOWLEDGE_UPDATED = "KNOWLEDGE_UPDATED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_DENIED = "APPROVAL_DENIED"


class AutonomyEvent(BaseModel):
    event_id: str
    event_type: AutonomyEventType
    source: str
    tenant_id: str = "default_tenant"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class EventEngine:
    """Reactive Event Bus for autonomous execution subscriptions and correlation."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._history: List[AutonomyEvent] = []

    def subscribe(self, event_type: AutonomyEventType, callback: Callable[[AutonomyEvent], None]) -> None:
        key = event_type.value
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(callback)

    def publish(self, event: AutonomyEvent) -> None:
        self._history.append(event)
        key = event.event_type.value
        listeners = self._listeners.get(key, [])
        logger.debug(f"[EVENT ENGINE] Published event '{event.event_type.value}' from '{event.source}'")
        for cb in listeners:
            try:
                cb(event)
            except Exception as ex:
                logger.warning(f"Error in event listener for '{key}': {ex}")

    def replay_events(self, tenant_id: str) -> List[AutonomyEvent]:
        return [e for e in self._history if e.tenant_id == tenant_id]
