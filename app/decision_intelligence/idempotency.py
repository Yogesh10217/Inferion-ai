"""
Decision Idempotency Subsystem.
Guarantees idempotent decision execution and recommendation generation based on SHA-256 request signatures.
"""

import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class DecisionIdempotencyStore:
    """Stores execution keys and results for idempotent operations."""

    def __init__(self) -> None:
        self._keys: Dict[str, Dict[str, Any]] = {}

    def compute_key(self, tenant_id: str, payload: Dict[str, Any]) -> str:
        canonical = json.dumps({"tenant_id": tenant_id, "payload": payload}, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def get_result(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        entry = self._keys.get(idempotency_key)
        return entry["result"] if entry else None

    def store_result(self, idempotency_key: str, result: Dict[str, Any]) -> None:
        self._keys[idempotency_key] = {"result": result, "stored_at": datetime.now(timezone.utc).isoformat()}
