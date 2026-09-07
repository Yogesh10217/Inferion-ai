"""Security Evidence Manager (Immutable Record Invariant)."""

import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_assurance.exceptions import ImmutableSecurityRecordException, CrossTenantSecurityAssuranceException

logger = logging.getLogger(__name__)


class SecurityEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"sec-ev-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    evidence_type: str  # INCIDENT_RECORD, POSTURE_SNAPSHOT, AUDIT_TRAIL, REMEDIATION_PROOF
    payload: Dict[str, Any]
    sha256_hash: str
    is_finalized: bool = False
    idempotency_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityEvidenceManager:
    """Manages creation, SHA-256 integrity verification, and immutability for security evidence records."""

    def __init__(self) -> None:
        self._evidence: Dict[str, SecurityEvidence] = {}
        self._idempotency_map: Dict[str, str] = {}

    def _compute_hash(self, tenant_id: str, evidence_type: str, payload: Dict[str, Any]) -> str:
        serialized = json.dumps({"tenant_id": tenant_id, "evidence_type": evidence_type, "payload": payload}, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def record_evidence(
        self,
        tenant_id: str,
        evidence_type: str,
        payload: Dict[str, Any],
        idempotency_key: Optional[str] = None,
    ) -> SecurityEvidence:
        if idempotency_key and idempotency_key in self._idempotency_map:
            existing_id = self._idempotency_map[idempotency_key]
            return self.get_evidence(tenant_id, existing_id)

        sha256_hash = self._compute_hash(tenant_id, evidence_type, payload)
        ev = SecurityEvidence(
            tenant_id=tenant_id,
            evidence_type=evidence_type,
            payload=payload,
            sha256_hash=sha256_hash,
            is_finalized=True,  # Immutably finalized upon creation
            idempotency_key=idempotency_key,
        )

        self._evidence[ev.evidence_id] = ev
        if idempotency_key:
            self._idempotency_map[idempotency_key] = ev.evidence_id
        logger.info(f"[SECURITY EVIDENCE] Recorded immutable evidence {ev.evidence_id} (SHA-256: {sha256_hash[:8]}...)")
        return ev

    def get_evidence(self, tenant_id: str, evidence_id: str) -> SecurityEvidence:
        ev = self._evidence.get(evidence_id)
        if not ev:
            raise KeyError(f"Evidence '{evidence_id}' not found.")
        if ev.tenant_id != tenant_id:
            raise CrossTenantSecurityAssuranceException(f"Tenant '{tenant_id}' cannot access evidence for tenant '{ev.tenant_id}'.")
        return ev

    def update_evidence(self, tenant_id: str, evidence_id: str, payload: Dict[str, Any]) -> SecurityEvidence:
        ev = self.get_evidence(tenant_id, evidence_id)
        if ev.is_finalized:
            raise ImmutableSecurityRecordException(f"Security evidence '{evidence_id}' is finalized and immutable.")
        ev.payload = payload
        ev.sha256_hash = self._compute_hash(tenant_id, ev.evidence_type, payload)
        return ev

    def list_evidence(self, tenant_id: str) -> List[SecurityEvidence]:
        return [e for e in self._evidence.values() if e.tenant_id == tenant_id]
