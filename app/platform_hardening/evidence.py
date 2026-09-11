"""
Platform Hardening Evidence Ledger.
Generates and seals SHA-256 evidence records with tamper detection and immutability enforcement.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from app.platform_hardening.exceptions import ImmutablePlatformAuditRecordException
from app.platform_hardening.models import CertificationEvidence


class PlatformHardeningEvidenceLedger:
    """Manages cryptographic SHA-256 evidence records."""

    def __init__(self):
        self._sealed_evidence: Dict[str, CertificationEvidence] = {}

    def seal_evidence(
        self, tenant_id: str, audit_id: str, payload: Dict, previous_hash: Optional[str] = None
    ) -> CertificationEvidence:
        ev_id = f"ev-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        payload_str = json.dumps(payload, sort_keys=True)
        sha256_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        evidence = CertificationEvidence(
            evidence_id=ev_id,
            tenant_id=tenant_id,
            audit_id=audit_id,
            sha256_hash=sha256_hash,
            previous_hash=previous_hash,
            sealed_at=now,
            is_valid=True,
        )

        self._sealed_evidence[ev_id] = evidence
        return evidence

    def verify_evidence(self, evidence_id: str, payload: Dict) -> bool:
        ev = self._sealed_evidence.get(evidence_id)
        if not ev:
            return False

        payload_str = json.dumps(payload, sort_keys=True)
        computed_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        return computed_hash == ev.sha256_hash

    def update_evidence(self, evidence_id: str):
        if evidence_id in self._sealed_evidence:
            raise ImmutablePlatformAuditRecordException()
