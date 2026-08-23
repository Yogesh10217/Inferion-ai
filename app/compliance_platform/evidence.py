"""Enterprise Compliance Evidence Engine & Immutable Evidence Bundles."""

import hashlib
import json
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import (
    EvidenceNotFoundException,
    ImmutableEvidenceBundleException,
    CrossTenantComplianceAccessException,
)


class EvidenceType(str, Enum):
    AUDIT_EVENT = "AUDIT_EVENT"
    POLICY_DECISION = "POLICY_DECISION"
    APPROVAL_RECORD = "APPROVAL_RECORD"
    IDENTITY_EVENT = "IDENTITY_EVENT"
    DATA_GOVERNANCE_DECISION = "DATA_GOVERNANCE_DECISION"
    ARCHITECTURE_SNAPSHOT = "ARCHITECTURE_SNAPSHOT"
    DRIFT_RECORD = "DRIFT_RECORD"
    OPERATIONAL_INCIDENT = "OPERATIONAL_INCIDENT"
    DEPLOYMENT_HISTORY = "DEPLOYMENT_HISTORY"
    SECURITY_EVENT = "SECURITY_EVENT"
    HUMAN_ATTESTATION = "HUMAN_ATTESTATION"


class EvidenceSource(str, Enum):
    ADMINISTRATIVE_AUDIT_LEDGER = "ADMINISTRATIVE_AUDIT_LEDGER"
    CHANGE_HISTORY_TRACKER = "CHANGE_HISTORY_TRACKER"
    APPROVAL_ENGINE = "APPROVAL_ENGINE"
    DATA_GOVERNANCE_MANAGER = "DATA_GOVERNANCE_MANAGER"
    ARCHITECTURE_PLATFORM_MANAGER = "ARCHITECTURE_PLATFORM_MANAGER"
    ENTERPRISE_INTELLIGENCE_MANAGER = "ENTERPRISE_INTELLIGENCE_MANAGER"
    PLATFORM_OPERATIONS_MANAGER = "PLATFORM_OPERATIONS_MANAGER"
    GOVERNANCE_PLATFORM_MANAGER = "GOVERNANCE_PLATFORM_MANAGER"
    IDENTITY_SECURITY_MANAGER = "IDENTITY_SECURITY_MANAGER"
    OBSERVABILITY_SYSTEM = "OBSERVABILITY_SYSTEM"


class EvidenceStatus(str, Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class EvidenceIntegrity(BaseModel):
    hash_algorithm: str = "SHA-256"
    integrity_hash: str
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceReference(BaseModel):
    evidence_id: str
    source_system: EvidenceSource
    source_reference: str


class Evidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    subject_type: str
    subject_id: str
    evidence_type: EvidenceType
    source_system: EvidenceSource
    source_reference: str
    status: EvidenceStatus = EvidenceStatus.VALID
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: Optional[datetime] = None
    integrity: EvidenceIntegrity
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def sanitize_metadata(self) -> None:

        """Sanitize sensitive keys or secrets in evidence metadata."""
        secret_keys = {"password", "secret", "token", "api_key", "credentials", "private_key", "ssn"}
        sanitized = {}
        for k, v in self.metadata.items():
            if any(sk in k.lower() for sk in secret_keys):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = v
        self.metadata = sanitized


class EvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"bundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    evidence_ids: List[str] = Field(default_factory=list)
    bundle_fingerprint: str
    is_finalized: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceManager:
    """Manages compliance evidence items and immutable evidence bundles."""

    def __init__(self) -> None:
        self._evidence_store: Dict[str, Evidence] = {}
        self._bundles: Dict[str, EvidenceBundle] = {}

    def collect_evidence(
        self,
        tenant_id: str,
        subject_type: str,
        subject_id: str,
        evidence_type: EvidenceType,
        source_system: EvidenceSource,
        source_reference: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Evidence:
        eid = f"ev_{uuid.uuid4().hex[:12]}"
        meta = metadata or {}
        
        # Calculate SHA-256 integrity hash from canonical metadata & references
        canonical_str = json.dumps({"tenant_id": tenant_id, "subject_id": subject_id, "ref": source_reference, "type": evidence_type.value}, sort_keys=True)
        hash_val = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        evidence = Evidence(
            evidence_id=eid,
            tenant_id=tenant_id,
            subject_type=subject_type,
            subject_id=subject_id,
            evidence_type=evidence_type,
            source_system=source_system,
            source_reference=source_reference,
            integrity=EvidenceIntegrity(integrity_hash=hash_val),
            metadata=meta,
        )
        evidence.sanitize_metadata()
        self._evidence_store[eid] = evidence
        return evidence

    def get_evidence(self, evidence_id: str, tenant_id: str) -> Evidence:
        ev = self._evidence_store.get(evidence_id)
        if not ev:
            raise EvidenceNotFoundException(evidence_id=evidence_id, tenant_id=tenant_id)
        if ev.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=ev.tenant_id, resource_id=evidence_id)
        return ev

    def list_evidence_for_subject(self, tenant_id: str, subject_id: str) -> List[Evidence]:
        return [e for e in self._evidence_store.values() if e.tenant_id == tenant_id and e.subject_id == subject_id]

    def create_immutable_bundle(self, tenant_id: str, evidence_ids: List[str]) -> EvidenceBundle:
        # Generate SHA-256 fingerprint for bundle
        sorted_eids = sorted(evidence_ids)
        fingerprint = hashlib.sha256(json.dumps({"tenant": tenant_id, "ids": sorted_eids}).encode("utf-8")).hexdigest()

        bundle = EvidenceBundle(
            tenant_id=tenant_id,
            evidence_ids=sorted_eids,
            bundle_fingerprint=fingerprint,
            is_finalized=True,
        )
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def get_bundle(self, bundle_id: str, tenant_id: str) -> EvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            raise ImmutableEvidenceBundleException(bundle_id=bundle_id, tenant_id=tenant_id)
        if bundle.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=bundle.tenant_id, resource_id=bundle_id)
        return bundle
