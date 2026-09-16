"""Decision Evidence Subsystem with Secret Sanitization."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import CrossTenantDecisionAccessException, DecisionEvidenceException
from app.security.secrets import SecretManager


class EvidenceStrength(str, Enum):
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    CONCLUSIVE = "CONCLUSIVE"


class EvidenceReliability(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    AUDITED = "AUDITED"


class EvidenceReference(BaseModel):
    reference_id: str = Field(default_factory=lambda: f"evref_{uuid.uuid4().hex[:12]}")
    source_subsystem: str  # DATA_GOVERNANCE, ARCHITECTURE, COMPLIANCE, PORTFOLIO, FINOPS, OPERATIONS
    source_entity_id: str
    description: str
    strength: EvidenceStrength = EvidenceStrength.STRONG
    reliability: EvidenceReliability = EvidenceReliability.VERIFIED
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceCollection(BaseModel):
    collection_id: str = Field(default_factory=lambda: f"evcol_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    references: List[EvidenceReference] = Field(default_factory=list)
    quality_score: float = 90.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionEvidenceManager:
    """Manages collection, sanitization, and verification of decision evidence."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._collections: Dict[str, EvidenceCollection] = {}

    def collect_evidence(
        self,
        tenant_id: str,
        context_id: str,
        references: List[EvidenceReference],
    ) -> EvidenceCollection:
        # Sanitize metadata in references
        sanitized_refs = []
        for ref in references:
            sanitized_meta = dict(ref.metadata)
            for k, v in list(sanitized_meta.items()):
                if any(sec in k.lower() for sec in ["secret", "key", "token", "password", "credential"]):
                    sanitized_meta[k] = "[REDACTED]"
            ref_copy = ref.model_copy(update={"metadata": sanitized_meta})
            sanitized_refs.append(ref_copy)

        collection = EvidenceCollection(
            tenant_id=tenant_id,
            context_id=context_id,
            references=sanitized_refs,
            quality_score=95.0,
        )
        self._collections[collection.collection_id] = collection
        return collection

    def get_collection(self, collection_id: str, tenant_id: str) -> EvidenceCollection:
        col = self._collections.get(collection_id)
        if not col:
            raise DecisionEvidenceException(f"Evidence collection '{collection_id}' not found.")
        if col.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionAccessException(tenant_id, col.tenant_id)
        return col
