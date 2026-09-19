"""Knowledge provenance tracking across origin, chain, evidence, and verification."""

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeProvenanceNotFoundException,
)


class ProvenanceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    TAMPERED = "TAMPERED"
    DISPUTED = "DISPUTED"


class ProvenanceSource(BaseModel):
    source_id: str
    source_name: str
    authority_type: str = "VERIFIED"
    origin_uri: Optional[str] = None


class ProvenanceEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    signature: str = ""
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProvenanceChain(BaseModel):
    chain_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    steps: List[Dict[str, Any]] = Field(default_factory=list)


class KnowledgeProvenance(BaseModel):
    provenance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id: str
    origin_source: ProvenanceSource
    chain: ProvenanceChain = Field(default_factory=ProvenanceChain)
    status: ProvenanceStatus = ProvenanceStatus.VERIFIED
    evidence: List[ProvenanceEvidence] = Field(default_factory=list)
    fingerprint: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def sha256_fingerprint(self) -> str:
        return self.fingerprint or self.calculate_fingerprint()

    def calculate_fingerprint(self) -> str:
        data = f"{self.provenance_id}:{self.tenant_id}:{self.reference_id}:{self.status.value}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class KnowledgeProvenanceManager:
    """Manages lineage and provenance validation for enterprise knowledge assets."""

    def __init__(self) -> None:
        self._provenance_records: Dict[str, KnowledgeProvenance] = {}

    def record_provenance(
        self,
        tenant_id: str,
        reference_id: Optional[str] = None,
        origin_source: Optional[ProvenanceSource] = None,
        target_resource_id: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        chain: Optional[ProvenanceChain] = None,
        evidence: Optional[List[ProvenanceEvidence]] = None,
    ) -> KnowledgeProvenance:
        ref_id = target_resource_id or reference_id or "ref-1"

        if origin_source is None:
            first_source_name = sources[0].get("source_id", "src-raw") if sources else "src-raw"
            origin_source = ProvenanceSource(source_id=first_source_name, source_name=first_source_name)

        prov = KnowledgeProvenance(
            tenant_id=tenant_id,
            reference_id=ref_id,
            origin_source=origin_source,
            chain=chain
            or ProvenanceChain(steps=[{"step": 1, "action": "INGESTED", "source": origin_source.source_name}]),
            evidence=evidence or [],
        )
        prov.fingerprint = prov.calculate_fingerprint()
        self._provenance_records[prov.provenance_id] = prov
        return prov

    def validate_provenance(self, tenant_id: str, provenance_id: str) -> Any:
        prov = self.get_provenance(provenance_id=provenance_id, tenant_id=tenant_id)
        is_valid = prov.fingerprint == prov.calculate_fingerprint()
        return type("ProvenanceValidation", (), {"is_valid": is_valid, "provenance_id": prov.provenance_id})()

    def get_provenance(self, provenance_id: str, tenant_id: str) -> KnowledgeProvenance:
        prov = self._provenance_records.get(provenance_id)
        if not prov:
            raise KnowledgeProvenanceNotFoundException(f"Provenance '{provenance_id}' not found")
        if prov.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return prov

    def get_provenance_by_reference(self, reference_id: str, tenant_id: str) -> Optional[KnowledgeProvenance]:
        for p in self._provenance_records.values():
            if p.reference_id == reference_id:
                if p.tenant_id != tenant_id:
                    raise CrossTenantKnowledgeAssuranceException()
                return p
        return None
