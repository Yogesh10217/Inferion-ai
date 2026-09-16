"""Knowledge Source Registry Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeSourceNotFoundException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeSourceType(str, Enum):
    KNOWLEDGE_PLATFORM = "KNOWLEDGE_PLATFORM"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    DECISION_INTELLIGENCE = "DECISION_INTELLIGENCE"
    RELIABILITY_PLATFORM = "RELIABILITY_PLATFORM"
    SECURITY_INTELLIGENCE = "SECURITY_INTELLIGENCE"
    AI_LIFECYCLE = "AI_LIFECYCLE"
    EVENT_INTELLIGENCE = "EVENT_INTELLIGENCE"
    INTEGRATION = "INTEGRATION"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"
    ARCHITECTURE_PLATFORM = "ARCHITECTURE_PLATFORM"
    PORTFOLIO_PLATFORM = "PORTFOLIO_PLATFORM"


class KnowledgeSourceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SYNCING = "SYNCING"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"


class KnowledgeSourceCapability(str, Enum):
    SEARCH = "SEARCH"
    SEMANTIC = "SEMANTIC"
    GRAPH = "GRAPH"
    PROVENANCE = "PROVENANCE"
    CHANGE_STREAM = "CHANGE_STREAM"


class KnowledgeSourceReference(BaseModel):
    system_name: str
    endpoint_or_ref: str


class KnowledgeSource(BaseModel):
    source_id: str = Field(default_factory=lambda: f"ksrc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    source_type: KnowledgeSourceType
    status: KnowledgeSourceStatus = KnowledgeSourceStatus.ACTIVE
    capabilities: List[KnowledgeSourceCapability] = Field(default_factory=lambda: [KnowledgeSourceCapability.SEARCH])
    reference: KnowledgeSourceReference
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeSourceManager:
    """Manages references to external and internal knowledge sources without copying raw store data."""

    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeSource] = {}

    def register_source(
        self,
        tenant_id: str,
        name: str,
        source_type: KnowledgeSourceType = KnowledgeSourceType.KNOWLEDGE_PLATFORM,
        system_name: str = "KnowledgePlatform",
        endpoint_or_ref: str = "app.knowledge_platform",
        capabilities: Optional[List[KnowledgeSourceCapability]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeSource:
        sanitized_meta = SensitiveDataSanitizer.sanitize(metadata or {})
        ref = KnowledgeSourceReference(system_name=system_name, endpoint_or_ref=endpoint_or_ref)
        src = KnowledgeSource(
            tenant_id=tenant_id,
            name=name,
            source_type=source_type,
            capabilities=capabilities or [KnowledgeSourceCapability.SEARCH],
            reference=ref,
            metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
        )
        self._store[src.source_id] = src
        return src

    def get_source(self, source_id: str, tenant_id: str) -> KnowledgeSource:
        src = self._store.get(source_id)
        if not src:
            raise KnowledgeSourceNotFoundException(source_id)
        if src.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAccessException(tenant_id)
        return src

    def list_sources(self, tenant_id: str) -> List[KnowledgeSource]:
        return [s for s in self._store.values() if s.tenant_id == tenant_id]
