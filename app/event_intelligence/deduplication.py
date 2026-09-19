"""Event Deduplication & Idempotency Protection Subsystem (Phase 5.34)."""

from typing import Dict, Optional

from pydantic import BaseModel

from app.event_intelligence.events import EnterpriseEvent
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.idempotency import IdempotencyManager


class EventFingerprint(BaseModel):
    fingerprint_id: str
    tenant_id: str
    sha256_hash: str


class EventDuplicate(BaseModel):
    original_event_id: str
    duplicate_event_id: str


class EventDeduplicationResult(BaseModel):
    is_duplicate: bool
    fingerprint_hash: str
    existing_event_id: Optional[str] = None


class EventDeduplicator:
    """Deduplicates events using canonical payload fingerprints and enforces tenant-scoped idempotency."""

    def __init__(self, idempotency_manager: Optional[IdempotencyManager] = None) -> None:
        self.idempotency_manager = idempotency_manager or IdempotencyManager()
        self._seen_fingerprints: Dict[str, str] = {}  # (tenant_id, hash) -> event_id

    def process_deduplication(self, event: EnterpriseEvent) -> EventDeduplicationResult:
        fp_payload = {
            "source_id": event.source.source_id,
            "event_type": event.event_type.value,
            "payload": event.metadata.payload,
        }
        fp_hash = FingerprintGenerator.generate(fp_payload)
        key = f"{event.tenant_id}:{fp_hash}"

        if key in self._seen_fingerprints:
            orig_id = self._seen_fingerprints[key]
            return EventDeduplicationResult(is_duplicate=True, fingerprint_hash=fp_hash, existing_event_id=orig_id)

        if event.idempotency_reference:
            record = self.idempotency_manager.check_or_start(
                tenant_id=event.tenant_id,
                operation_type="PROCESS_ENTERPRISE_EVENT",
                idempotency_key=event.idempotency_reference,
                request_payload=fp_payload,
            )

            if record and record.result_payload and record.result_payload.get("event_id") != event.event_id:
                existing_id = record.result_payload.get("event_id")
                return EventDeduplicationResult(
                    is_duplicate=True, fingerprint_hash=fp_hash, existing_event_id=existing_id
                )

            self.idempotency_manager.complete_operation(
                tenant_id=event.tenant_id,
                operation_type="PROCESS_ENTERPRISE_EVENT",
                idempotency_key=event.idempotency_reference,
                result_payload={"event_id": event.event_id},
            )

        self._seen_fingerprints[key] = event.event_id
        return EventDeduplicationResult(is_duplicate=False, fingerprint_hash=fp_hash)
