"""SHA-256 Idempotency Deduplication Manager (Phase 5.58)."""

import hashlib
import json
import logging
from typing import Any, Dict, Set

logger = logging.getLogger(__name__)


class PlatformIntegrationIdempotencyManager:
    """Provides deterministic SHA-256 deduplication for cross-phase operations."""

    def __init__(self) -> None:
        self._seen_keys: Set[str] = set()

    def generate_key(self, tenant_id: str, operation: str, payload: Dict[str, Any]) -> str:
        data = {
            "tenant_id": tenant_id,
            "operation": operation,
            "payload": payload,
        }
        raw = json.dumps(data, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def check_and_record(self, key: str) -> bool:
        """Returns True if first time seen, False if duplicate."""
        if key in self._seen_keys:
            logger.warning(f"Duplicate operation detected for idempotency key: {key[:12]}...")
            return False
        self._seen_keys.add(key)
        return True
