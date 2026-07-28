import secrets
from typing import Any, Dict, List, Optional

from app.events.dead_letter_queue import DeadLetterQueue
from app.events.delivery_service import DeliveryService
from app.events.event_models import WebhookDelivery, WebhookEndpoint, WebhookEvent
from app.events.event_serializer import EventEnvelope
from app.events.event_storage import EventStorage


class WebhookService:
    """Unified management service for webhooks and event delivery."""

    def __init__(
        self,
        event_storage: EventStorage,
        delivery_service: DeliveryService,
        dead_letter_queue: DeadLetterQueue,
    ):
        self.storage = event_storage
        self.delivery_service = delivery_service
        self.dlq = dead_letter_queue

    # Endpoint CRUD
    async def create_endpoint(
        self,
        organization_id: str,
        url: str,
        event_types: List[str],
        secret: Optional[str] = None,
        enabled: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
    ) -> WebhookEndpoint:
        endpoint_secret = secret or secrets.token_hex(24)
        return await self.storage.create_endpoint(
            organization_id=organization_id,
            url=url,
            secret=endpoint_secret,
            event_types=event_types,
            enabled=enabled,
            retry_policy=retry_policy,
        )

    async def get_endpoint(self, endpoint_id: str) -> WebhookEndpoint:
        return await self.storage.get_endpoint(endpoint_id)

    async def list_endpoints(
        self, organization_id: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[WebhookEndpoint]:
        return await self.storage.list_endpoints(organization_id=organization_id, limit=limit, offset=offset)

    async def update_endpoint(self, endpoint_id: str, **kwargs) -> WebhookEndpoint:
        return await self.storage.update_endpoint(endpoint_id, **kwargs)

    async def rotate_secret(self, endpoint_id: str, new_secret: Optional[str] = None) -> WebhookEndpoint:
        """Rotate endpoint secret. Sets current secret to secondary_secret for dual-secret verification."""
        endpoint = await self.get_endpoint(endpoint_id)
        next_secret = new_secret or secrets.token_hex(24)
        
        return await self.storage.update_endpoint(
            endpoint_id,
            secret=next_secret,
            secondary_secret=endpoint.secret,
        )

    async def delete_endpoint(self, endpoint_id: str) -> bool:
        return await self.storage.delete_endpoint(endpoint_id)

    # Deliveries and Events query
    async def list_deliveries(
        self, endpoint_id: Optional[str] = None, status: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[WebhookDelivery]:
        return await self.storage.list_deliveries(endpoint_id=endpoint_id, status=status, limit=limit, offset=offset)

    async def list_events(
        self, organization_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[WebhookEvent]:
        return await self.storage.list_events(organization_id=organization_id, event_type=event_type, limit=limit, offset=offset)

    # Replay
    async def replay_delivery(self, delivery_id: str) -> WebhookDelivery:
        return await self.dlq.replay_delivery(delivery_id)

    # Dispatch event to matching endpoints
    async def process_published_event(self, envelope: EventEnvelope) -> List[WebhookDelivery]:
        """Persists event and dispatches delivery to all matching endpoints asynchronously."""
        # Stage 2: Persist event
        await self.storage.persist_event(envelope)

        # Find subscribed endpoints
        matching_endpoints = await self.storage.find_matching_endpoints(
            event_type=envelope.event_type, organization_id=envelope.organization_id
        )

        deliveries = []
        for ep in matching_endpoints:
            # Deliver to each endpoint asynchronously (endpoint isolation)
            delivery = await self.delivery_service.deliver_event_to_endpoint(ep, envelope)
            deliveries.append(delivery)

        return deliveries
