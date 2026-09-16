"""
Idempotency & Deduplication Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Enforces idempotency across signal ingestion, situation updates, recommendation generation,
and delegation requests using SHA-256 fingerprinting.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.unified_intelligence.exceptions import InvalidUnifiedIntelligenceInputException


class IdempotencyEngine:
    """
    Deduplicates incoming signals and operations via idempotency keys and sliding time windows.
    """

    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl_seconds = default_ttl_seconds
        # Mapping: tenant_id:idempotency_key -> (result_data, expiration_time)
        self._cache: Dict[str, tuple[Any, datetime]] = {}

    def generate_fingerprint(self, payload: Dict[str, Any]) -> str:
        """
        Generates a deterministic SHA-256 fingerprint for any JSON-serializable payload.
        """
        canonical_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def is_duplicate(
        self,
        tenant_id: str,
        idempotency_key: str
    ) -> bool:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if not idempotency_key:
            return False

        cache_key = f"{tenant_id}:{idempotency_key}"
        entry = self._cache.get(cache_key)
        if not entry:
            return False

        _, expiry = entry
        if datetime.utcnow() > expiry:
            del self._cache[cache_key]
            return False
        return True

    def register_execution(
        self,
        tenant_id: str,
        idempotency_key: str,
        result_data: Any,
        ttl_seconds: Optional[int] = None
    ) -> None:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if not idempotency_key:
            return

        ttl = ttl_seconds or self.default_ttl_seconds
        cache_key = f"{tenant_id}:{idempotency_key}"
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._cache[cache_key] = (result_data, expiry)

    def get_cached_result(
        self,
        tenant_id: str,
        idempotency_key: str
    ) -> Optional[Any]:
        if not tenant_id or not idempotency_key:
            return None
        cache_key = f"{tenant_id}:{idempotency_key}"
        entry = self._cache.get(cache_key)
        if not entry:
            return None
        result, expiry = entry
        if datetime.utcnow() > expiry:
            del self._cache[cache_key]
            return None
        return result
