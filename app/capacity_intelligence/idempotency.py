"""SHA-256 idempotency manager for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import Set

logger = logging.getLogger(__name__)


class CapacityIdempotencyManager:
    """Enforces SHA-256 idempotency key deduplication across telemetry, forecasts, and recommendations."""

    def __init__(self) -> None:
        self._seen_keys: Set[str] = set()

    def check_and_record(self, idempotency_key: str) -> bool:
        if idempotency_key in self._seen_keys:
            logger.warning(f"Duplicate capacity operation blocked by idempotency key: {idempotency_key[:12]}...")
            return False
        self._seen_keys.add(idempotency_key)
        return True
