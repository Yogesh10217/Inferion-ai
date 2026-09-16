"""Runtime Context Policy Engine for Phase 5.57 Runtime Intelligence."""

import hashlib
import json
import logging
from typing import Any, Dict

from app.platform_contracts.sanitizer import SensitiveDataSanitizer
from app.runtime_intelligence.limits import RuntimeLimitsManager

logger = logging.getLogger(__name__)


class RuntimeContextPolicyEngine:
    """Enforces bounded context size and calculates canonical SHA-256 context fingerprints."""

    def sanitize_and_fingerprint(
        self, tenant_id: str, raw_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # 1. Sanitize sensitive data
        sanitized = SensitiveDataSanitizer.sanitize(raw_context)

        # 2. Enforce limits
        RuntimeLimitsManager.validate_context_limit(len(sanitized))

        # 3. Generate SHA-256 fingerprint
        canonical_bytes = json.dumps(sanitized, sort_keys=True, default=str).encode("utf-8")
        fingerprint = hashlib.sha256(canonical_bytes).hexdigest()

        return {
            "tenant_id": tenant_id,
            "context_data": sanitized,
            "context_fingerprint": fingerprint,
        }
