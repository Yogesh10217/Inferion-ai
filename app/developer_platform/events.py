"""Developer Events & Webhooks Platform with HMAC SHA-256 signing and DLQ."""

import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.developer_platform.exceptions import EventSubscriptionNotFoundException
from app.jobs.job_queue import Job, JobQueue
from app.resilience.circuit_breaker import CircuitBreakerRegistry

logger = logging.getLogger(__name__)


class DeveloperEvent(BaseModel):
    """Event emitted across platform execution pipelines."""

    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(default_factory=lambda: f"idemp_{uuid.uuid4().hex[:10]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WebhookSubscription(BaseModel):
    """Webhook delivery target configuration."""

    subscription_id: str = Field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    developer_id: str
    target_url: str
    secret_key: str = Field(default_factory=lambda: f"whsec_{uuid.uuid4().hex[:16]}")
    event_types: List[str] = Field(default_factory=list)
    is_active: bool = True
    max_retries: int = 5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeliveryRecord(BaseModel):
    """Audit log entry for a webhook delivery attempt."""

    delivery_id: str = Field(default_factory=lambda: f"dlv_{uuid.uuid4().hex[:10]}")
    subscription_id: str
    event_id: str
    status_code: int
    success: bool
    attempt: int
    signature: str
    delivered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeveloperEventEngine:
    """Dispatches events, signs payloads with HMAC SHA-256, and routes failed deliveries to DLQ."""

    def __init__(
        self,
        circuit_breakers: Optional[CircuitBreakerRegistry] = None,
        job_queue: Optional[JobQueue] = None,
    ) -> None:
        self.circuit_breakers = circuit_breakers or CircuitBreakerRegistry()
        self.job_queue = job_queue or JobQueue()
        self._subscriptions: Dict[str, WebhookSubscription] = {}
        self._delivery_logs: List[DeliveryRecord] = []

    def create_subscription(
        self,
        developer_id: str,
        target_url: str,
        event_types: List[str],
        tenant_id: str = "global",
    ) -> WebhookSubscription:
        """Register a new webhook subscription."""
        sub = WebhookSubscription(
            developer_id=developer_id,
            target_url=target_url,
            event_types=event_types,
            tenant_id=tenant_id,
        )
        self._subscriptions[sub.subscription_id] = sub
        logger.info(f"[EVENT ENGINE] Created webhook subscription '{sub.subscription_id}' for URL '{target_url}'")
        return sub

    def get_subscription(self, subscription_id: str) -> WebhookSubscription:
        sub = self._subscriptions.get(subscription_id)
        if not sub:
            raise EventSubscriptionNotFoundException(subscription_id)
        return sub

    def delete_subscription(self, subscription_id: str) -> bool:
        self.get_subscription(subscription_id)
        del self._subscriptions[subscription_id]
        logger.info(f"[EVENT ENGINE] Deleted subscription '{subscription_id}'")
        return True

    def list_subscriptions(
        self, tenant_id: Optional[str] = None, developer_id: Optional[str] = None
    ) -> List[WebhookSubscription]:
        res = list(self._subscriptions.values())
        if tenant_id:
            res = [s for s in res if s.tenant_id in (tenant_id, "global")]
        if developer_id:
            res = [s for s in res if s.developer_id == developer_id]
        return res

    @staticmethod
    def sign_payload(payload_bytes: bytes, secret_key: str) -> str:
        """Compute HMAC SHA-256 signature for payload integrity & authenticity."""
        return hmac.new(secret_key.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    def dispatch_event(self, event: DeveloperEvent) -> List[DeliveryRecord]:
        """Dispatch event to all matching active webhook subscriptions."""
        deliveries = []
        matching = [
            s
            for s in self._subscriptions.values()
            if s.is_active
            and s.tenant_id in (event.tenant_id, "global")
            and (event.event_type in s.event_types or "*" in s.event_types)
        ]

        for sub in matching:
            rec = self._deliver_to_subscription(sub, event)
            deliveries.append(rec)

        return deliveries

    def _deliver_to_subscription(
        self, sub: WebhookSubscription, event: DeveloperEvent, attempt: int = 1
    ) -> DeliveryRecord:
        """Simulate secure delivery with HMAC signature generation and DLQ backup on failure."""
        payload_str = str(event.payload).encode("utf-8")
        sig = self.sign_payload(payload_str, sub.secret_key)

        # High reliability check
        cb = self.circuit_breakers.get_breaker(f"webhook:{sub.subscription_id}")
        if not cb.allow_request():
            logger.warning(f"[EVENT ENGINE] Circuit breaker OPEN for webhook '{sub.subscription_id}', routing to DLQ")
            self._route_to_dlq(sub, event, "Circuit breaker OPEN")
            rec = DeliveryRecord(
                subscription_id=sub.subscription_id,
                event_id=event.event_id,
                status_code=503,
                success=False,
                attempt=attempt,
                signature=sig,
            )
            self._delivery_logs.append(rec)
            return rec

        # Successful simulation delivery
        cb.record_success()
        rec = DeliveryRecord(
            subscription_id=sub.subscription_id,
            event_id=event.event_id,
            status_code=200,
            success=True,
            attempt=attempt,
            signature=sig,
        )
        self._delivery_logs.append(rec)

        logger.info(f"[EVENT ENGINE] Delivered event '{event.event_type}' to '{sub.target_url}' (Sig: {sig[:8]}...)")
        return rec

    def _route_to_dlq(self, sub: WebhookSubscription, event: DeveloperEvent, reason: str) -> None:
        """Route failed webhook delivery to Dead-Letter Queue (DLQ)."""
        job = Job(
            job_type="webhook_dlq",
            tenant_id=sub.tenant_id,
            payload={"subscription_id": sub.subscription_id, "event": event.model_dump(), "reason": reason},
            max_attempts=sub.max_retries,
        )
        self.job_queue.enqueue(job)
        logger.error(f"[EVENT DLQ] Enqueued failed webhook '{sub.subscription_id}' to DLQ: {reason}")
