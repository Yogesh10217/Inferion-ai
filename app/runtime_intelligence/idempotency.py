"""SHA-256 idempotency manager for Runtime Intelligence (Phase 5.57)."""

import hashlib
import json
import logging
import threading
from typing import Set, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RuntimeIdempotencyManager:
    """Enforces SHA-256 idempotency key deduplication to prevent duplicate processing."""

    def __init__(self) -> None:
        self._seen_keys: Set[str] = set()
        self._lock = threading.RLock()

    def generate_key(self, tenant_id: str, operation_name: str, payload: Dict[str, Any]) -> str:
        serialized = json.dumps({"tenant": tenant_id, "op": operation_name, "data": payload}, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def check_and_record(self, idempotency_key: str) -> bool:
        with self._lock:
            if idempotency_key in self._seen_keys:
                logger.warning(f"Duplicate operation blocked by idempotency key: {idempotency_key[:12]}...")
                return False
            self._seen_keys.add(idempotency_key)
            return True
