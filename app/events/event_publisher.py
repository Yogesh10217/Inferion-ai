import logging
from typing import Any, Dict, Optional

from app.events.event_bus import IEventBus
from app.events.event_registry import EventRegistry
from app.events.event_serializer import EventEnvelope
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class EventPublisher:
    """High-level event publisher interface."""

    def __init__(self, event_bus: IEventBus, metrics_service: Optional[MetricsService] = None):
        self.event_bus = event_bus
        self.metrics_service = metrics_service

    async def publish(
        self,
        event_type: str,
        payload: Dict[str, Any],
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        actor: Optional[str] = None,
        source: str = "llm-inference-engine",
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
    ) -> EventEnvelope:
        """Constructs standardized envelope and publishes to event bus."""
        event_def = EventRegistry.get_event(event_type)
        schema_ver = version or (event_def.version if event_def else "1.0")

        envelope = EventEnvelope(
            event_type=event_type,
            payload=payload,
            version=schema_ver,
            organization_id=organization_id,
            workspace_id=workspace_id,
            actor=actor,
            source=source,
            correlation_id=correlation_id,
            request_id=request_id,
            metadata=metadata,
        )

        await self.event_bus.publish(envelope)

        if self.metrics_service:
            if hasattr(self.metrics_service, "record_event_published"):
                self.metrics_service.record_event_published(event_type)

        logger.debug(f"Event published: {event_type} ({envelope.event_id})")
        return envelope
