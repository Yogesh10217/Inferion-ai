"""Knowledge Normalization Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.knowledge_intelligence.knowledge import KnowledgeItem
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeNormalizationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"normrule_{uuid.uuid4().hex[:8]}")
    field_name: str
    action: str = "STANDARDIZE"


class NormalizedKnowledge(BaseModel):
    normalized_id: str = Field(default_factory=lambda: f"normk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    item_id: str
    canonical_title: str
    canonical_type: str
    canonical_classification: str
    normalized_metadata: Dict[str, Any]
    fingerprint: str
    normalized_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeNormalizationResult(BaseModel):
    normalized_knowledge: NormalizedKnowledge
    rules_applied: List[str] = Field(default_factory=list)


class KnowledgeNormalizer:
    """Provides deterministic knowledge metadata normalization and canonical fingerprinting."""

    def normalize(self, tenant_id: str, knowledge_item: KnowledgeItem) -> KnowledgeNormalizationResult:
        sanitized_attrs = SensitiveDataSanitizer.sanitize(knowledge_item.metadata.attributes)

        canonical_title = knowledge_item.metadata.title.strip()
        canonical_type = knowledge_item.knowledge_type.value
        canonical_classification = knowledge_item.classification.value

        normalized_metadata = {
            "title": canonical_title,
            "type": canonical_type,
            "classification": canonical_classification,
            "domain": knowledge_item.metadata.domain.upper(),
            "tags": sorted(knowledge_item.metadata.tags),
            "attributes": sanitized_attrs if isinstance(sanitized_attrs, dict) else {},
        }

        fp_payload = {
            "tenant_id": tenant_id,
            "item_id": knowledge_item.item_id,
            "canonical_title": canonical_title,
            "canonical_type": canonical_type,
            "normalized_metadata": normalized_metadata,
        }
        fp_hash = FingerprintGenerator.generate(fp_payload)

        norm = NormalizedKnowledge(
            tenant_id=tenant_id,
            item_id=knowledge_item.item_id,
            canonical_title=canonical_title,
            canonical_type=canonical_type,
            canonical_classification=canonical_classification,
            normalized_metadata=normalized_metadata,
            fingerprint=fp_hash,
        )

        return KnowledgeNormalizationResult(
            normalized_knowledge=norm,
            rules_applied=["STANDARDIZE_TITLE", "SORT_TAGS", "UPPERCASE_DOMAIN", "CANONICAL_FINGERPRINT"],
        )
