"""Enterprise Knowledge Registry Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeNotFoundException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeType(str, Enum):
    DOCUMENT = "DOCUMENT"
    DECISION = "DECISION"
    EVENT = "EVENT"
    INCIDENT = "INCIDENT"
    SECURITY_FINDING = "SECURITY_FINDING"
    MODEL = "MODEL"
    DATASET = "DATASET"
    AGENT = "AGENT"
    ARCHITECTURE = "ARCHITECTURE"
    POLICY = "POLICY"
    PROCEDURE = "PROCEDURE"
    EVIDENCE = "EVIDENCE"
    INSIGHT = "INSIGHT"
    PATTERN = "PATTERN"
    RECOMMENDATION = "RECOMMENDATION"


class KnowledgeStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    STALE = "STALE"
    RETIRED = "RETIRED"
    SUPERSEDES = "SUPERSEDES"


class KnowledgeClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    CRITICAL = "CRITICAL"


class KnowledgeOrigin(str, Enum):
    INTERNAL = "INTERNAL"
    DERIVED = "DERIVED"
    EXTERNAL = "EXTERNAL"
    SYNTHETIC = "SYNTHETIC"
    HUMAN_INPUT = "HUMAN_INPUT"


class KnowledgeMetadata(BaseModel):
    title: str = "Untitled Knowledge"
    summary: str = ""
    domain: str = "GENERAL"
    tags: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    author: Optional[str] = None
    version: str = "1.0.0"


class KnowledgeReference(BaseModel):
    source_system: str
    external_id: str
    uri: Optional[str] = None


class KnowledgeItem(BaseModel):
    item_id: str = Field(default_factory=lambda: f"kitem_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    classification: KnowledgeClassification = KnowledgeClassification.INTERNAL
    origin: KnowledgeOrigin = KnowledgeOrigin.INTERNAL
    metadata: KnowledgeMetadata = Field(default_factory=KnowledgeMetadata)
    reference: Optional[KnowledgeReference] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeManager:
    """Manages enterprise knowledge registration and metadata lookups with strict tenant isolation."""

    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeItem] = {}

    def register_knowledge(
        self,
        tenant_id: str,
        title: str,
        knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT,
        classification: KnowledgeClassification = KnowledgeClassification.INTERNAL,
        origin: KnowledgeOrigin = KnowledgeOrigin.INTERNAL,
        source_system: str = "INTERNAL",
        external_id: str = "",
        tags: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeItem:
        sanitized_attrs = SensitiveDataSanitizer.sanitize(attributes or {})
        metadata = KnowledgeMetadata(
            title=title,
            tags=tags or [],
            attributes=sanitized_attrs if isinstance(sanitized_attrs, dict) else {},
        )
        ref = KnowledgeReference(source_system=source_system, external_id=external_id or uuid.uuid4().hex[:8])
        item = KnowledgeItem(
            tenant_id=tenant_id,
            knowledge_type=knowledge_type,
            classification=classification,
            origin=origin,
            metadata=metadata,
            reference=ref,
        )
        self._store[item.item_id] = item
        return item

    def get_knowledge(self, item_id: str, tenant_id: str) -> KnowledgeItem:
        item = self._store.get(item_id)
        if not item:
            raise KnowledgeNotFoundException(item_id)
        if item.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAccessException(tenant_id)
        return item

    def list_knowledge(
        self,
        tenant_id: str,
        knowledge_type: Optional[KnowledgeType] = None,
    ) -> List[KnowledgeItem]:
        results = [i for i in self._store.values() if i.tenant_id == tenant_id]
        if knowledge_type:
            results = [i for i in results if i.knowledge_type == knowledge_type]
        return results

    def update_status(self, item_id: str, tenant_id: str, new_status: KnowledgeStatus) -> KnowledgeItem:
        item = self.get_knowledge(item_id, tenant_id)
        item.status = new_status
        item.updated_at = datetime.now(timezone.utc)
        return item
