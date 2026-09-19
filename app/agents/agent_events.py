"""
Agent Events Publisher
"""

import logging
from typing import Any, Dict, Optional

from app.agents.agent_context import AgentContext
from app.events.event_bus import IEventBus, InMemoryEventBus
from app.events.event_serializer import EventEnvelope

logger = logging.getLogger(__name__)

# Global or default EventBus instance
_global_event_bus: Optional[IEventBus] = None


def get_event_bus() -> IEventBus:
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = InMemoryEventBus()
    return _global_event_bus


def set_event_bus(bus: IEventBus) -> None:
    global _global_event_bus
    _global_event_bus = bus


async def emit_agent_event(
    event_type: str, context: AgentContext, payload: Dict[str, Any], event_bus: Optional[IEventBus] = None
) -> EventEnvelope:
    bus = event_bus or get_event_bus()
    envelope = EventEnvelope(
        event_type=event_type,
        payload=payload,
        organization_id=context.organization_id,
        workspace_id=context.workspace_id,
        actor=context.user_id,
        source="agent_framework",
        metadata=context.metadata,
    )
    try:
        await bus.publish(envelope)
    except Exception as e:
        logger.warning(f"Failed to publish agent event {event_type}: {e}")
    return envelope
