"""Unified Idempotency Framework (Phase 5.30)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.exceptions import IdempotencyConflictException
from app.platform_contracts.fingerprinting import FingerprintGenerator


class IdempotencyStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    COMPENSATED = "COMPENSATED"


class IdempotencyKey(BaseModel):
    key: str
    tenant_id: str
    operation_type: str


class IdempotencyRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"idemp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    operation_type: str
    idempotency_key: str
    request_fingerprint: str
    status: IdempotencyStatus = IdempotencyStatus.PENDING
    result_payload: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdempotencyManager:
    """Manages idempotent operation replay and conflict resolution across tenant boundaries."""

    def __init__(self) -> None:
        # Keyed by (tenant_id, operation_type, idempotency_key)
        self._store: Dict[str, IdempotencyRecord] = {}

    def _make_lookup_key(self, tenant_id: str, operation_type: str, idempotency_key: str) -> str:
        return f"{tenant_id}::{operation_type}::{idempotency_key}"

    def check_or_start(
        self,
        tenant_id: str,
        operation_type: str,
        idempotency_key: str,
        request_payload: Any,
    ) -> Optional[IdempotencyRecord]:
        lookup_key = self._make_lookup_key(tenant_id, operation_type, idempotency_key)
        payload_fp = FingerprintGenerator.generate(request_payload)

        existing = self._store.get(lookup_key)
        if existing:
            if existing.request_fingerprint != payload_fp:
                raise IdempotencyConflictException(idempotency_key, operation_type)
            return existing

        # Create new record
        record = IdempotencyRecord(
            tenant_id=tenant_id,
            operation_type=operation_type,
            idempotency_key=idempotency_key,
            request_fingerprint=payload_fp,
            status=IdempotencyStatus.RUNNING,
        )
        self._store[lookup_key] = record
        return None

    def complete_operation(
        self,
        tenant_id: str,
        operation_type: str,
        idempotency_key: str,
        result_payload: Dict[str, Any],
        status: IdempotencyStatus = IdempotencyStatus.COMPLETED,
    ) -> IdempotencyRecord:
        lookup_key = self._make_lookup_key(tenant_id, operation_type, idempotency_key)
        record = self._store.get(lookup_key)
        if not record:
            record = IdempotencyRecord(
                tenant_id=tenant_id,
                operation_type=operation_type,
                idempotency_key=idempotency_key,
                request_fingerprint="",
                status=status,
            )
            self._store[lookup_key] = record

        record.status = status
        record.result_payload = result_payload
        record.updated_at = datetime.now(timezone.utc)
        return record
