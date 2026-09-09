"""SHA-256 idempotency manager for Reliability Intelligence (Phase 5.55)."""

import hashlib
import json
import threading
from typing import Dict, Any, Optional

class ReliabilityIdempotencyManager:
    """Prevents duplicate predictions, recommendations, delegations, evidence, recovery plans, and degradation plans."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._keys: Dict[str, Dict[str, Any]] = {}

    def generate_key(self, tenant_id: str, operation_type: str, payload: Dict[str, Any]) -> str:
        canonical = json.dumps({"tenant_id": tenant_id, "operation_type": operation_type, "payload": payload}, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def register_operation(self, key: str, result: Dict[str, Any]) -> bool:
        with self._lock:
            if key in self._keys:
                return False
            self._keys[key] = result
            return True

    def get_existing_result(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._keys.get(key)
