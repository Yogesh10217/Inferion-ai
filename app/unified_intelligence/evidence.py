"""
SHA-256 Immutable Evidence Ledger Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Generates and seals tamper-evident audit packages with SHA-256 verification,
raising ImmutableUnifiedIntelligenceRecordException if mutations are attempted on finalized records.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json
import uuid

from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException,
    ImmutableUnifiedIntelligenceRecordException
)


class UnifiedEvidenceRecord:
    """
    Immutable evidence record representing cryptographic proof of cross-domain decisions.
    """
    def __init__(
        self,
        evidence_id: str,
        tenant_id: str,
        source_domain: str,
        payload: Dict[str, Any],
        sha256_hash: str,
        finalized: bool = True,
        created_at: Optional[datetime] = None
    ):
        self.evidence_id = evidence_id
        self.tenant_id = tenant_id
        self.source_domain = source_domain
        self.payload = payload
        self.sha256_hash = sha256_hash
        self.finalized = finalized
        self.created_at = created_at or datetime.utcnow()

    def update_payload(self, new_payload: Dict[str, Any]):
        if self.finalized:
            raise ImmutableUnifiedIntelligenceRecordException(
                f"Cannot modify evidence record {self.evidence_id} in tenant {self.tenant_id}: record is finalized and immutable."
            )
        self.payload = new_payload

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "tenant_id": self.tenant_id,
            "source_domain": self.source_domain,
            "payload": self.payload,
            "sha256_hash": self.sha256_hash,
            "finalized": self.finalized,
            "created_at": self.created_at.isoformat()
        }


class SHA256EvidenceLedgerEngine:
    """
    Cryptographic SHA-256 evidence ledger for cross-domain unified intelligence.
    """
    def __init__(self):
        self._ledger: Dict[str, UnifiedEvidenceRecord] = {}

    def create_evidence(
        self,
        tenant_id: str,
        source_domain: str,
        payload: Dict[str, Any]
    ) -> UnifiedEvidenceRecord:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        ev_id = f"ev-{uuid.uuid4().hex[:12]}"
        canonical_str = json.dumps(payload, sort_keys=True, default=str)
        hash_val = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        record = UnifiedEvidenceRecord(
            evidence_id=ev_id,
            tenant_id=tenant_id,
            source_domain=source_domain,
            payload=payload,
            sha256_hash=hash_val,
            finalized=True
        )
        self._ledger[ev_id] = record
        return record

    def get_evidence(self, tenant_id: str, evidence_id: str) -> UnifiedEvidenceRecord:
        record = self._ledger.get(evidence_id)
        if not record:
            raise InvalidUnifiedIntelligenceInputException(f"Evidence record {evidence_id} not found.")
        if record.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch for evidence record {evidence_id}: expected {tenant_id}, got {record.tenant_id}"
            )
        return record

    def verify_integrity(self, evidence_id: str) -> bool:
        record = self._ledger.get(evidence_id)
        if not record:
            return False
        canonical_str = json.dumps(record.payload, sort_keys=True, default=str)
        calc_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        return calc_hash == record.sha256_hash
