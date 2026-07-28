from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.event_models import DeadLetterEvent, WebhookDelivery, WebhookEndpoint, WebhookEvent
from app.events.event_serializer import EventEnvelope
from app.events.exceptions import EndpointNotFoundException


class EventStorage:
    """Async database repository for webhook endpoints, events, deliveries, and dead letter events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Webhook Endpoints ---

    async def create_endpoint(
        self,
        organization_id: str,
        url: str,
        secret: str,
        event_types: List[str],
        enabled: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
        secondary_secret: Optional[str] = None,
    ) -> WebhookEndpoint:
        endpoint = WebhookEndpoint(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            url=url,
            secret=secret,
            secondary_secret=secondary_secret,
            enabled=enabled,
            event_types=event_types,
            retry_policy=retry_policy,
        )
        self.db.add(endpoint)
        await self.db.commit()
        await self.db.refresh(endpoint)
        return endpoint

    async def get_endpoint(self, endpoint_id: str) -> WebhookEndpoint:
        endpoint = await self.db.get(WebhookEndpoint, endpoint_id)
        if not endpoint:
            raise EndpointNotFoundException(f"WebhookEndpoint {endpoint_id} not found")
        return endpoint

    async def list_endpoints(
        self, organization_id: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[WebhookEndpoint]:
        stmt = select(WebhookEndpoint)
        if organization_id:
            stmt = stmt.where(WebhookEndpoint.organization_id == organization_id)
        stmt = stmt.limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_endpoint(self, endpoint_id: str, **kwargs) -> WebhookEndpoint:
        endpoint = await self.get_endpoint(endpoint_id)
        for key, val in kwargs.items():
            if hasattr(endpoint, key) and val is not None:
                setattr(endpoint, key, val)
        await self.db.commit()
        await self.db.refresh(endpoint)
        return endpoint

    async def delete_endpoint(self, endpoint_id: str) -> bool:
        endpoint = await self.get_endpoint(endpoint_id)
        await self.db.delete(endpoint)
        await self.db.commit()
        return True

    async def find_matching_endpoints(
        self, event_type: str, organization_id: Optional[str] = None
    ) -> List[WebhookEndpoint]:
        """Find active endpoints subscribed to event_type or wildcard '*'."""
        stmt = select(WebhookEndpoint).where(WebhookEndpoint.enabled == True)
        if organization_id:
            stmt = stmt.where(WebhookEndpoint.organization_id == organization_id)
        res = await self.db.execute(stmt)
        all_endpoints = res.scalars().all()

        matching = []
        for ep in all_endpoints:
            types = ep.event_types or []
            if "*" in types or event_type in types:
                matching.append(ep)
        return matching

    # --- Webhook Events ---

    async def persist_event(self, envelope: EventEnvelope) -> WebhookEvent:
        event = WebhookEvent(
            id=envelope.event_id,
            event_type=envelope.event_type,
            version=envelope.version,
            organization_id=envelope.organization_id,
            workspace_id=envelope.workspace_id,
            actor=envelope.actor,
            source=envelope.source,
            correlation_id=envelope.correlation_id,
            request_id=envelope.request_id,
            payload=envelope.payload,
            metadata_json=envelope.metadata,
            timestamp=datetime.fromisoformat(envelope.timestamp)
            if isinstance(envelope.timestamp, str)
            else envelope.timestamp,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_event(self, event_id: str) -> Optional[WebhookEvent]:
        return await self.db.get(WebhookEvent, event_id)

    async def list_events(
        self, organization_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[WebhookEvent]:
        stmt = select(WebhookEvent)
        if organization_id:
            stmt = stmt.where(WebhookEvent.organization_id == organization_id)
        if event_type:
            stmt = stmt.where(WebhookEvent.event_type == event_type)
        stmt = stmt.order_by(WebhookEvent.timestamp.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # --- Webhook Deliveries ---

    async def create_delivery(
        self, endpoint_id: str, event_id: str, is_replay: bool = False
    ) -> WebhookDelivery:
        delivery = WebhookDelivery(
            id=str(uuid.uuid4()),
            endpoint_id=endpoint_id,
            event_id=event_id,
            status="pending",
            attempts=0,
            is_replay=is_replay,
        )
        self.db.add(delivery)
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def update_delivery(
        self,
        delivery_id: str,
        status: str,
        attempts: int,
        latency_ms: Optional[int] = None,
        response_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> WebhookDelivery:
        delivery = await self.db.get(WebhookDelivery, delivery_id)
        if not delivery:
            raise EndpointNotFoundException(f"Delivery {delivery_id} not found")

        delivery.status = status
        delivery.attempts = attempts
        if latency_ms is not None:
            delivery.latency_ms = latency_ms
        if response_code is not None:
            delivery.response_code = response_code
        if response_body is not None:
            delivery.response_body = response_body
        if status == "success":
            delivery.delivered_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def get_delivery(self, delivery_id: str) -> Optional[WebhookDelivery]:
        return await self.db.get(WebhookDelivery, delivery_id)

    async def list_deliveries(
        self, endpoint_id: Optional[str] = None, status: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[WebhookDelivery]:
        stmt = select(WebhookDelivery)
        if endpoint_id:
            stmt = stmt.where(WebhookDelivery.endpoint_id == endpoint_id)
        if status:
            stmt = stmt.where(WebhookDelivery.status == status)
        stmt = stmt.order_by(WebhookDelivery.created_at.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # --- Dead Letter Queue ---

    async def create_dead_letter(
        self, delivery_id: str, endpoint_id: str, event_id: str, reason: str, payload: Dict[str, Any]
    ) -> DeadLetterEvent:
        dlq = DeadLetterEvent(
            id=str(uuid.uuid4()),
            delivery_id=delivery_id,
            endpoint_id=endpoint_id,
            event_id=event_id,
            reason=reason,
            payload=payload,
            failed_at=datetime.now(timezone.utc),
        )
        self.db.add(dlq)
        await self.db.commit()
        await self.db.refresh(dlq)
        return dlq

    async def get_dead_letter_count(self) -> int:
        res = await self.db.execute(select(func.count(DeadLetterEvent.id)))
        return res.scalar() or 0

    async def list_dead_letters(self, limit: int = 100, offset: int = 0) -> List[DeadLetterEvent]:
        stmt = select(DeadLetterEvent).order_by(DeadLetterEvent.failed_at.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
