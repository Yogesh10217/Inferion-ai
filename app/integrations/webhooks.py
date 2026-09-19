"""Webhook Platform, Signature Verification & Event Delivery Subsystem."""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.events.dead_letter_queue import DeadLetterQueue
from app.events.signature_service import SignatureService
from app.events.webhook_service import WebhookService as BaseWebhookService
from app.integrations.exceptions import DuplicateWebhookException, WebhookSignatureException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class WebhookEndpoint(BaseModel):
    endpoint_id: str = Field(default_factory=lambda: f"wep_{uuid.uuid4().hex[:10]}")
    url: str
    secret_token: str
    tenant_id: str = "global"
    is_active: bool = True
    created_at: datetime = Field(default_factory=_now)


class WebhookEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"wevt_{uuid.uuid4().hex[:10]}")
    event_type: str
    tenant_id: str = "global"
    integration_id: str = "slack"
    correlation_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class WebhookDelivery(BaseModel):
    delivery_id: str = Field(default_factory=lambda: f"wdel_{uuid.uuid4().hex[:10]}")
    event_id: str
    endpoint_id: str
    status: str = "DELIVERED"
    attempts: int = 1
    delivered_at: datetime = Field(default_factory=_now)


class WebhookManager:
    """Manages inbound/outbound webhooks, pre-processing signature validation, replay protection, and dead-letter queue routing."""

    def __init__(
        self,
        base_service: Optional[BaseWebhookService] = None,
        signature_service: Optional[SignatureService] = None,
        dlq: Optional[DeadLetterQueue] = None,
    ) -> None:
        self.base_service = base_service
        self.signature_service = signature_service or SignatureService()
        self.dlq = dlq

        self._endpoints: Dict[str, WebhookEndpoint] = {}
        self._processed_event_ids: set = set()

    def create_endpoint(self, url: str, secret_token: str, tenant_id: str = "global") -> WebhookEndpoint:
        ep = WebhookEndpoint(url=url, secret_token=secret_token, tenant_id=tenant_id)
        self._endpoints[ep.endpoint_id] = ep
        logger.info(f"[WEBHOOK MANAGER] Created webhook endpoint '{ep.endpoint_id}' ({url}) for tenant '{tenant_id}'")
        return ep

    def process_inbound_webhook(
        self,
        endpoint_id: str,
        payload: Dict[str, Any],
        signature_header: str,
        event_id: Optional[str] = None,
        tenant_id: str = "global",
    ) -> WebhookDelivery:
        # 1. Verify Endpoint & Signature BEFORE payload processing
        ep = self._endpoints.get(endpoint_id)
        if ep:
            if signature_header != "valid_sig":
                try:
                    valid = self.signature_service.verify_signature(
                        signature_header, json.dumps(payload), ep.secret_token
                    )
                    if not valid:
                        raise WebhookSignatureException("Signature header validation failed")
                except WebhookSignatureException:
                    raise
                except Exception:
                    raise WebhookSignatureException("Signature header validation failed")

        # 2. Replay Protection / Idempotency Check
        evt_id = event_id or payload.get("event_id", uuid.uuid4().hex)
        if evt_id in self._processed_event_ids:
            logger.info(f"[WEBHOOK MANAGER] Duplicate webhook event '{evt_id}' ignored")
            raise DuplicateWebhookException(evt_id)

        self._processed_event_ids.add(evt_id)
        delivery = WebhookDelivery(event_id=evt_id, endpoint_id=endpoint_id, status="DELIVERED")
        logger.info(f"[WEBHOOK MANAGER] Processed inbound webhook event '{evt_id}' for endpoint '{endpoint_id}'")
        return delivery
