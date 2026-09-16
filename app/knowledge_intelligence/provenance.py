"""Knowledge Provenance Engine Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
)
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.redaction import SensitiveDataSanitizer


class ProvenanceType(str, Enum):
    SOURCE = "SOURCE"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    HUMAN_VALIDATED = "HUMAN_VALIDATED"
    SYSTEM_GENERATED = "SYSTEM_GENERATED"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"


class ProvenanceReference(BaseModel):
    upstream_id: str
    upstream_type: str = "UNKNOWN"
    relationship_to_source: str = "DERIVED_FROM"


class ProvenanceRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"provrec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    provenance_type: ProvenanceType
    upstream_references: List[ProvenanceReference] = Field(default_factory=list)
    agent_or_user_id: Optional[str] = None
    transformation_description: str = "Direct Reference"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    fingerprint: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProvenanceChain(BaseModel):
    chain_id: str = Field(default_factory=lambda: f"provchain_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    root_source_id: str
    records: List[ProvenanceRecord] = Field(default_factory=list)
    chain_fingerprint: str = ""


class ProvenanceIntegrity(BaseModel):
    is_valid: bool
    calculated_fingerprint: str
    expected_fingerprint: str
    verification_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeProvenance(BaseModel):
    provenance_id: str = Field(default_factory=lambda: f"kprov_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    item_id: str
    chain: ProvenanceChain


class KnowledgeProvenanceManager:
    """Manages lineage, evidence references, and SHA-256 fingerprinted provenance chains."""

    def __init__(self) -> None:
        self._records: Dict[str, ProvenanceRecord] = {}

    def record_provenance(
        self,
        tenant_id: str,
        target_id: str,
        provenance_type: ProvenanceType = ProvenanceType.SOURCE,
        upstream_references: Optional[List[ProvenanceReference]] = None,
        transformation_description: str = "Registered source material",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceRecord:
        sanitized_meta = SensitiveDataSanitizer.sanitize(metadata or {})
        refs = upstream_references or []

        fp_payload = {
            "tenant_id": tenant_id,
            "target_id": target_id,
            "provenance_type": provenance_type.value,
            "upstream_references": [r.model_dump() for r in refs],
            "transformation": transformation_description,
        }
        fp_hash = FingerprintGenerator.generate(fp_payload)

        rec = ProvenanceRecord(
            tenant_id=tenant_id,
            target_id=target_id,
            provenance_type=provenance_type,
            upstream_references=refs,
            transformation_description=transformation_description,
            metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
            fingerprint=fp_hash,
        )
        self._records[rec.record_id] = rec
        return rec

    def get_provenance_chain(self, target_id: str, tenant_id: str) -> ProvenanceChain:
        records = [r for r in self._records.values() if r.target_id == target_id and r.tenant_id == tenant_id]
        if not records:
            # Check cross tenant leak
            cross_check = [r for r in self._records.values() if r.target_id == target_id]
            if cross_check:
                raise CrossTenantKnowledgeAccessException(tenant_id)
            root_id = target_id
        else:
            root_id = records[0].upstream_references[0].upstream_id if records[0].upstream_references else target_id

        chain_payload = {
            "tenant_id": tenant_id,
            "target_id": target_id,
            "record_ids": [r.record_id for r in records],
        }
        chain_fp = FingerprintGenerator.generate(chain_payload)

        return ProvenanceChain(
            tenant_id=tenant_id,
            root_source_id=root_id,
            records=records,
            chain_fingerprint=chain_fp,
        )

    def verify_integrity(self, record: ProvenanceRecord) -> ProvenanceIntegrity:
        fp_payload = {
            "tenant_id": record.tenant_id,
            "target_id": record.target_id,
            "provenance_type": record.provenance_type.value,
            "upstream_references": [r.model_dump() for r in record.upstream_references],
            "transformation": record.transformation_description,
        }
        calc_fp = FingerprintGenerator.generate(fp_payload)
        is_valid = calc_fp == record.fingerprint
        return ProvenanceIntegrity(
            is_valid=is_valid,
            calculated_fingerprint=calc_fp,
            expected_fingerprint=record.fingerprint,
        )
