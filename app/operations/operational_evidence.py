"""
Operational Evidence Module for Phase 5.68.
Collects, sanitizes, formats deterministically, and fingerprints operational telemetry with SHA-256 hashes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from app.deployment.secrets import SecretsSanitizer


@dataclass
class OperationalEvidence:
    evidence_id: str
    timestamp: str
    evidence_level: str
    canonical_payload: Dict[str, Any]
    sha256_fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "timestamp": self.timestamp,
            "evidence_level": self.evidence_level,
            "canonical_payload": self.canonical_payload,
            "sha256_fingerprint": self.sha256_fingerprint,
        }


class OperationalEvidenceCollector:
    """Collects and generates immutable SHA-256 fingerprinted operational evidence records."""

    def create_evidence(
        self,
        raw_payload: Dict[str, Any],
        evidence_level: str = "CONTAINER_RUNTIME",
        evidence_id: str = "ev-568-001",
    ) -> OperationalEvidence:
        now_iso = datetime.now(timezone.utc).isoformat()

        # Step 1: SecretsSanitizer
        sanitized_payload = SecretsSanitizer.sanitize_structure(raw_payload)

        # Step 2: Canonical Payload
        canonical = {
            "evidence_id": evidence_id,
            "evidence_level": evidence_level,
            "data": sanitized_payload,
        }

        # Step 3: Deterministic JSON (sorted keys)
        deterministic_json = json.dumps(canonical, sort_keys=True)

        # Step 4: SHA-256 Fingerprint
        fingerprint = hashlib.sha256(deterministic_json.encode("utf-8")).hexdigest()

        return OperationalEvidence(
            evidence_id=evidence_id,
            timestamp=now_iso,
            evidence_level=evidence_level,
            canonical_payload=canonical,
            sha256_fingerprint=fingerprint,
        )
