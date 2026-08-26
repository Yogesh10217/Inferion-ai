"""Knowledge Evidence Management Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.evidence import (
    EvidenceReference,
    EvidenceMetadata,
    EvidenceSourceReference,
    EvidenceStrength,
    EvidenceIntegrity,
)
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeEvidenceStrength(str, Enum):
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    CONCLUSIVE = "CONCLUSIVE"


class KnowledgeEvidenceIntegrity(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    AUDITED = "AUDITED"


class KnowledgeEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"kev_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    evidence_ref: EvidenceReference
    summary: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"kevbundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    items: List[KnowledgeEvidence] = Field(default_factory=list)
    bundle_fingerprint: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeEvidenceManager:
    """Manages evidence collection, references, and bundle fingerprinting for knowledge items."""

    def __init__(self) -> None:
        self._bundles: Dict[str, KnowledgeEvidenceBundle] = {}

    def create_evidence(
        self,
        tenant_id: str,
        target_id: str,
        source_subsystem: str = "KnowledgePlatform",
        source_entity_id: str = "",
        summary: str = "Knowledge Grounding Evidence",
        strength: EvidenceStrength = EvidenceStrength.STRONG,
    ) -> KnowledgeEvidence:
        meta = EvidenceMetadata(
            tenant_id=tenant_id,
            source=EvidenceSourceReference(
                source_subsystem=source_subsystem,
                source_entity_id=source_entity_id or target_id,
            ),
            strength=strength,
            integrity=EvidenceIntegrity.VERIFIED,
        )
        ref = EvidenceReference(metadata=meta, description=summary)

        return KnowledgeEvidence(
            tenant_id=tenant_id,
            target_id=target_id,
            evidence_ref=ref,
            summary=summary,
        )

    def assemble_bundle(self, tenant_id: str, target_id: str, items: List[KnowledgeEvidence]) -> KnowledgeEvidenceBundle:
        fp_payload = {
            "tenant_id": tenant_id,
            "target_id": target_id,
            "evidence_ids": [i.evidence_id for i in items],
        }
        fp_hash = FingerprintGenerator.generate(fp_payload)
        bundle = KnowledgeEvidenceBundle(
            tenant_id=tenant_id,
            target_id=target_id,
            items=items,
            bundle_fingerprint=fp_hash,
        )
        self._bundles[bundle.bundle_id] = bundle
        return bundle
