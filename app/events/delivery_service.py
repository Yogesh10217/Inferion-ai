import asyncio
import logging
import time
from typing import Optional

import httpx

from app.events.event_models import WebhookDelivery, WebhookEndpoint
from app.events.event_serializer import EventEnvelope
from app.events.event_storage import EventStorage
from app.events.retry_policy import RetryPolicy
from app.events.signature_service import SignatureService
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class DeliveryService:
    """
    Handles HTTP POST webhook delivery.
    Implements staged pipeline: Publish -> Persist -> Queue -> Attempt -> Retry -> Dead-Letter.
    """

    def __init__(
        self,
        event_storage: EventStorage,
        metrics_service: Optional[MetricsService] = None,
        http_timeout: float = 10.0,
    ):
        self.storage = event_storage
        self.metrics_service = metrics_service
        self.http_timeout = http_timeout

    async def deliver_event_to_endpoint(
        self,
        endpoint: WebhookEndpoint,
        envelope: EventEnvelope,
        is_replay: bool = False,
    ) -> WebhookDelivery:
        """
        Stage 3: Queue Delivery -> Stage 4: Delivery Attempt -> Stage 5: Retry -> Stage 6: DLQ
        """
        # Create initial pending delivery record
        delivery = await self.storage.create_delivery(
            endpoint_id=endpoint.id,
            event_id=envelope.event_id,
            is_replay=is_replay,
        )

        retry_policy = RetryPolicy.from_dict(endpoint.retry_policy)
        payload_str = envelope.to_json()

        attempts = 0
        success = False
        last_status_code: Optional[int] = None
        last_response_body: Optional[str] = None
        total_latency_ms = 0

        while attempts < retry_policy.max_retries:
            attempts += 1
            headers = SignatureService.generate_headers(
                event_id=envelope.event_id,
                event_type=envelope.event_type,
                secret=endpoint.secret,
                payload=payload_str,
            )
            # Add idempotency key
            headers["X-Idempotency-Key"] = f"{envelope.event_id}:{endpoint.id}:{attempts}"

            start_time = time.time()

            try:
                async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                    response = await client.post(endpoint.url, content=payload_str, headers=headers)
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    total_latency_ms += elapsed_ms

                    last_status_code = response.status_code
                    last_response_body = response.text[:2000]  # truncate if very large

                    if 200 <= response.status_code < 300:
                        success = True
                        break

            except Exception as exc:
                elapsed_ms = int((time.time() - start_time) * 1000)
                total_latency_ms += elapsed_ms
                last_status_code = None
                last_response_body = f"Network/HTTP Exception: {str(exc)}"
                logger.warning(
                    f"Webhook delivery attempt {attempts}/{retry_policy.max_retries} failed for endpoint {endpoint.id}: {exc}"
                )

            # Check if retry should be attempted
            if retry_policy.should_retry(attempts, last_status_code):
                delay_ms = retry_policy.calculate_delay_ms(attempts)
                if self.metrics_service and hasattr(self.metrics_service, "record_webhook_retry"):
                    self.metrics_service.record_webhook_retry()
                await asyncio.sleep(delay_ms / 1000.0)
            else:
                break

        # Final delivery outcome update
        final_status = "success" if success else "failed"
        updated_delivery = await self.storage.update_delivery(
            delivery_id=delivery.id,
            status=final_status,
            attempts=attempts,
            latency_ms=total_latency_ms,
            response_code=last_status_code,
            response_body=last_response_body,
        )

        # Update observability metrics
        if self.metrics_service and hasattr(self.metrics_service, "record_webhook_delivery"):
            self.metrics_service.record_webhook_delivery(latency_ms=float(total_latency_ms), success=success)

        # Stage 6: Dead-letter queue if delivery failed after max retries
        if not success:
            reason = f"Exhausted {attempts} retries. Last status: {last_status_code}. Body: {last_response_body}"
            await self.storage.create_dead_letter(
                delivery_id=delivery.id,
                endpoint_id=endpoint.id,
                event_id=envelope.event_id,
                reason=reason,
                payload=envelope.to_dict(),
            )
            if self.metrics_service and hasattr(self.metrics_service, "record_dead_letter_event"):
                self.metrics_service.record_dead_letter_event()

        return updated_delivery
