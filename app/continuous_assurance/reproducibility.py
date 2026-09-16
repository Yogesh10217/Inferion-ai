"""Reproducibility record generator for Continuous Assurance (Phase 5.54)."""

import hashlib
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ContinuousAssuranceReproducibilityRecord:
    """Captures observation fingerprints, evidence hashes, baseline versions, and SHA-256 reproducibility hash."""

    def generate_reproducibility_record(
        self, tenant_id: str, baseline_version: int, evidence_hashes: list
    ) -> Dict[str, Any]:
        payload = {
            "tenant_id": tenant_id,
            "baseline_version": baseline_version,
            "evidence_hashes": evidence_hashes,
        }
        canonical = json.dumps(payload, sort_keys=True)
        sha256_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return {
            "reproducibility_id": f"rep_{sha256_hash[:12]}",
            "tenant_id": tenant_id,
            "baseline_version": baseline_version,
            "sha256_hash": sha256_hash,
            "payload": payload,
        }
