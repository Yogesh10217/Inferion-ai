import asyncio
import logging
from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.events.dead_letter_queue import DeadLetterQueue
from app.events.delivery_service import DeliveryService
from app.events.event_bus import IEventBus
from app.events.event_serializer import EventEnvelope
from app.events.event_storage import EventStorage
from app.events.webhook_service import WebhookService
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class EventDispatcher:
    """Subscribes to EventBus and triggers WebhookService processing asynchronously."""

    def __init__(
        self,
        event_bus: IEventBus,
        session_factory: Callable[[], AsyncSession],
        metrics_service: Optional[MetricsService] = None,
    ):
        self.event_bus = event_bus
        self.session_factory = session_factory
        self.metrics_service = metrics_service
        self._subscribed = False

    def start(self) -> None:
        """Subscribe to wildcard '*' events on event bus."""
        if not self._subscribed:
            self.event_bus.subscribe("*", self._handle_event)
            self._subscribed = True
            logger.info("EventDispatcher subscribed to EventBus (*)")

    def stop(self) -> None:
        if self._subscribed:
            self.event_bus.unsubscribe("*", self._handle_event)
            self._subscribed = False
            logger.info("EventDispatcher unsubscribed from EventBus (*)")

    async def _handle_event(self, envelope: EventEnvelope) -> None:
        """Handle incoming event in isolated task with fresh DB session."""
        asyncio.create_task(self._process_event_async(envelope))

    async def _process_event_async(self, envelope: EventEnvelope) -> None:
        try:
            async with self.session_factory() as session:
                storage = EventStorage(session)
                delivery_svc = DeliveryService(storage, metrics_service=self.metrics_service)
                dlq = DeadLetterQueue(storage, delivery_svc, metrics_service=self.metrics_service)
                webhook_svc = WebhookService(storage, delivery_svc, dlq)

                await webhook_svc.process_published_event(envelope)
        except Exception as exc:
            logger.error(
                f"EventDispatcher error processing event {envelope.event_type} ({envelope.event_id}): {exc}",
                exc_info=True,
            )
