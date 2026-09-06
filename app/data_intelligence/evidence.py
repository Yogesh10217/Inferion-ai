"""Enterprise data evidence management (Phase 5.43)."""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import (
    ImmutableDataRecordException,
    CrossTenantDataIntelligenceException,
)
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.redaction import SensitiveDataSanitizer


class DataEvidenceIntegrity(BaseModel):
    sha256_hash: str
    is_finalized: bool = True
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataEvidence(BaseModel):
    evidence_id: str
    tenant_id: str
    dataset_id: str
    evidence_type: str  # QUALITY, ANOMALY, DRIFT, FRESHNESS, LINEAGE, INCIDENT
    reference_id: str
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)
    integrity: DataEvidenceIntegrity
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataEvidenceBundle(BaseModel):
    bundle_id: str
    tenant_id: str
    dataset_id: str
    evidences: List[DataEvidence] = Field(default_factory=list)
    bundle_fingerprint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataEvidenceManager:
    """Manages immutable finalized data evidence bundles with SHA-256 integrity."""

    def __init__(self) -> None:
        self._evidences: Dict[str, DataEvidence] = {}
        self._bundles: Dict[str, DataEvidenceBundle] = {}
        self._sanitizer = SensitiveDataSanitizer()

    def record_evidence(
        self,
        tenant_id: str,
        dataset_id: str,
        evidence_type: str,
        reference_id: str,
        raw_metadata: Optional[Dict[str, Any]] = None,
        evidence_id: Optional[str] = None,
    ) -> DataEvidence:
        eid = evidence_id or f"devid-{uuid.uuid4().hex[:8]}"

        sanitized_meta = self._sanitizer.sanitize(raw_metadata or {})
        clean_meta = sanitized_meta if isinstance(sanitized_meta, dict) else {}

        fp = FingerprintGenerator.generate({"tenant_id": tenant_id, "dataset_id": dataset_id, "evidence_type": evidence_type, "meta": clean_meta})

        ev = DataEvidence(
            evidence_id=eid,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            evidence_type=evidence_type,
            reference_id=reference_id,
            sanitized_metadata=clean_meta,
            integrity=DataEvidenceIntegrity(sha256_hash=fp, is_finalized=True),
        )
        self._evidences[eid] = ev
        return ev

    def create_bundle(
        self,
        tenant_id: str,
        dataset_id: str,
        evidence_ids: List[str],
        bundle_id: Optional[str] = None,
    ) -> DataEvidenceBundle:
        bid = bundle_id or f"dbundle-{uuid.uuid4().hex[:8]}"

        ev_list = []
        for eid in evidence_ids:
            ev = self.get_evidence(eid, tenant_id)
            ev_list.append(ev)

        bundle_fp = FingerprintGenerator.generate({
            "tenant_id": tenant_id,
            "dataset_id": dataset_id,
            "evidences": [e.evidence_id for e in ev_list],
        })

        bundle = DataEvidenceBundle(
            bundle_id=bid,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            evidences=ev_list,
            bundle_fingerprint=bundle_fp,
        )
        self._bundles[bid] = bundle
        return bundle

    def get_evidence(self, evidence_id: str, tenant_id: str) -> DataEvidence:
        ev = self._evidences.get(evidence_id)
        if not ev:
            raise Exception(f"Evidence '{evidence_id}' not found.")
        if ev.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return ev

    def verify_integrity(self, evidence_id: str, tenant_id: str) -> bool:
        ev = self.get_evidence(evidence_id, tenant_id)
        computed_fp = FingerprintGenerator.generate({
            "tenant_id": tenant_id,
            "dataset_id": ev.dataset_id,
            "evidence_type": ev.evidence_type,
            "meta": ev.sanitized_metadata,
        })
        return computed_fp == ev.integrity.sha256_hash
