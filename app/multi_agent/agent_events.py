"""
Multi-Agent Event Registry and Dispatcher
"""

import time
import logging
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)


class MultiAgentEventRegistry:
    TEAM_CREATED = "multi_agent.team.created"
    TEAM_STARTED = "multi_agent.team.started"
    TEAM_DELEGATION = "multi_agent.team.delegation"
    TEAM_HANDOFF = "multi_agent.team.handoff"
    TEAM_CONSENSUS = "multi_agent.team.consensus"
    TEAM_NEGOTIATION = "multi_agent.team.negotiation"
    TEAM_COMPLETED = "multi_agent.team.completed"
    TEAM_FAILED = "multi_agent.team.failed"


class MultiAgentEventDispatcher:
    """Dispatches multi-agent team lifecycle events to listeners."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def dispatch(self, event_type: str, payload: Dict[str, Any]) -> None:
        listeners = self._listeners.get(event_type, [])
        event_data = {
            "event_type": event_type,
            "timestamp": time.time(),
            "payload": payload,
        }
        for cb in listeners:
            try:
                cb(event_data)
            except Exception as e:
                logger.warning(f"Error executing event listener for '{event_type}': {e}")
