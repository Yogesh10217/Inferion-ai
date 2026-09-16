"""Immutable operational evidence management with SHA-256 verification and tenant isolation."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import (
    CrossTenantOperationsAssuranceException,
    ImmutableOperationalRecordException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class OperationalEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    evidence_type: str
    content: Dict[str, Any]
    sha256_hash: str = ""
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_hash(self) -> str:
        data_str = json.dumps(self.content, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


class OperationalEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    evidence_items: List[OperationalEvidence] = Field(default_factory=list)
    bundle_hash: str = ""
    is_finalized: bool = False
    finalized_at: Optional[datetime] = None


class OperationalEvidenceIntegrity(BaseModel):
    evidence_id: str
    tenant_id: str
    is_valid: bool
    computed_hash: str
    stored_hash: str
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalEvidenceManager:
    """Manages immutable operational evidence records with SHA-256 integrity checks."""

    def __init__(self) -> None:
        self._evidence: Dict[str, Dict[str, OperationalEvidence]] = {}  # tenant_id -> {id: evidence}
        self._bundles: Dict[str, Dict[str, OperationalEvidenceBundle]] = {}  # tenant_id -> {id: bundle}

    def record_evidence(
        self,
        tenant_id: str,
        service_id: str,
        evidence_type: str,
        content: Dict[str, Any],
    ) -> OperationalEvidence:
        sanitized_content = SensitiveDataSanitizer.sanitize_metadata(content)
        ev = OperationalEvidence(
            tenant_id=tenant_id,
            service_id=service_id,
            evidence_type=evidence_type,
            content=sanitized_content,
        )
        ev.sha256_hash = ev.compute_hash()
        ev.is_finalized = True  # Finalized upon record

        if tenant_id not in self._evidence:
            self._evidence[tenant_id] = {}
        self._evidence[tenant_id][ev.evidence_id] = ev
        return ev

    def update_evidence(self, tenant_id: str, evidence_id: str, new_content: Dict[str, Any]) -> None:
        ev = self.get_evidence(tenant_id, evidence_id)
        if ev.is_finalized:
            raise ImmutableOperationalRecordException("Cannot modify finalized operational evidence record.")

    def get_evidence(self, tenant_id: str, evidence_id: str) -> OperationalEvidence:
        if tenant_id not in self._evidence or evidence_id not in self._evidence[tenant_id]:
            for tid, items in self._evidence.items():
                if tid != tenant_id and evidence_id in items:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise CrossTenantOperationsAssuranceException("Evidence not found.")
        return self._evidence[tenant_id][evidence_id]

    def verify_integrity(self, tenant_id: str, evidence_id: str) -> OperationalEvidenceIntegrity:
        ev = self.get_evidence(tenant_id, evidence_id)
        computed = ev.compute_hash()
        is_valid = computed == ev.sha256_hash
        return OperationalEvidenceIntegrity(
            evidence_id=ev.evidence_id,
            tenant_id=tenant_id,
            is_valid=is_valid,
            computed_hash=computed,
            stored_hash=ev.sha256_hash,
        )
