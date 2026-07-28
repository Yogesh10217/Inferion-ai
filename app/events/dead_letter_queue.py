from datetime import datetime, timezone
import logging
from typing import List, Optional

from app.events.delivery_service import DeliveryService
from app.events.event_models import DeadLetterEvent, WebhookDelivery
from app.events.event_serializer import EventEnvelope
from app.events.event_storage import EventStorage
from app.events.exceptions import EndpointNotFoundException
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class DeadLetterQueue:
    """Manages dead-letter events and event replay execution."""

    def __init__(
        self,
        event_storage: EventStorage,
        delivery_service: DeliveryService,
        metrics_service: Optional[MetricsService] = None,
    ):
        self.storage = event_storage
        self.delivery_service = delivery_service
        self.metrics_service = metrics_service

    async def get_dead_letter(self, delivery_id: str) -> Optional[DeadLetterEvent]:
        deliveries = await self.storage.list_dead_letters(limit=1000)
        for dl in deliveries:
            if dl.delivery_id == delivery_id:
                return dl
        return None

    async def replay_delivery(self, delivery_id: str) -> WebhookDelivery:
        """
        Replay a delivery attempt.
        Creates a new WebhookDelivery record while preserving the original WebhookEvent
        and complete historical delivery records.
        """
        delivery = await self.storage.get_delivery(delivery_id)
        if not delivery:
            raise EndpointNotFoundException(f"Original WebhookDelivery {delivery_id} not found")

        endpoint = await self.storage.get_endpoint(delivery.endpoint_id)
        event_model = await self.storage.get_event(delivery.event_id)

        if not event_model:
            raise EndpointNotFoundException(f"Original WebhookEvent {delivery.event_id} not found")

        # Convert stored model back into EventEnvelope
        envelope = EventEnvelope(
            event_id=event_model.id,
            event_type=event_model.event_type,
            version=event_model.version,
            organization_id=event_model.organization_id,
            workspace_id=event_model.workspace_id,
            actor=event_model.actor,
            source=event_model.source,
            correlation_id=event_model.correlation_id,
            request_id=event_model.request_id,
            payload=event_model.payload,
            metadata=event_model.metadata_json or {},
        )

        # Update dead letter entry if present
        dlq_entry = await self.get_dead_letter(delivery_id)
        if dlq_entry:
            dlq_entry.replay_count += 1
            dlq_entry.replayed_at = datetime.now(timezone.utc)
            await self.storage.db.commit()

        # Update replay count metric
        if self.metrics_service and hasattr(self.metrics_service, "record_webhook_replay"):
            self.metrics_service.record_webhook_replay()

        # Execute replay delivery attempt (is_replay=True creates a brand NEW WebhookDelivery)
        new_delivery = await self.delivery_service.deliver_event_to_endpoint(
            endpoint=endpoint,
            envelope=envelope,
            is_replay=True,
        )

        logger.info(f"Replayed delivery {delivery_id} for endpoint {endpoint.id} -> new delivery {new_delivery.id}")
        return new_delivery

    async def list_dead_letters(self, limit: int = 100, offset: int = 0) -> List[DeadLetterEvent]:
        return await self.storage.list_dead_letters(limit=limit, offset=offset)
