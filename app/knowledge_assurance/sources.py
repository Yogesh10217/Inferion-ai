"""Knowledge source intelligence for evaluating authority, reliability, and freshness."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeSourceNotFoundException,
)


class KnowledgeSourceType(str, Enum):
    INTERNAL_DOCS = "INTERNAL_DOCS"
    DATABASE = "DATABASE"
    API = "API"
    REPOSITORY = "REPOSITORY"
    EXTERNAL_SEARCH = "EXTERNAL_SEARCH"
    CONFLUENCE = "CONFLUENCE"
    NOTION = "NOTION"
    GITHUB = "GITHUB"
    SHAREPOINT = "SHAREPOINT"


class KnowledgeSourceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEGRADED = "DEGRADED"
    REVOKED = "REVOKED"


class KnowledgeSourceAuthority(str, Enum):
    AUTHORITATIVE = "AUTHORITATIVE"
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    THIRD_PARTY = "THIRD_PARTY"


class KnowledgeSourceReliability(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class KnowledgeSource(BaseModel):
    source_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.INTERNAL_DOCS
    status: KnowledgeSourceStatus = KnowledgeSourceStatus.ACTIVE
    authority: KnowledgeSourceAuthority = KnowledgeSourceAuthority.VERIFIED
    reliability: KnowledgeSourceReliability = KnowledgeSourceReliability.HIGH
    trust_score: float = 0.90
    last_verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def reliability_score(self) -> float:
        return self.trust_score


class KnowledgeSourceManager:
    """Manages knowledge source authority and reliability evaluation."""

    def __init__(self) -> None:
        self._sources: Dict[str, KnowledgeSource] = {}

    def register_source(
        self,
        tenant_id: str,
        name: str,
        source_type: Any = KnowledgeSourceType.INTERNAL_DOCS,
        authority: Any = KnowledgeSourceAuthority.VERIFIED,
        reliability: Any = KnowledgeSourceReliability.HIGH,
        reliability_score: Optional[float] = None,
        trust_score: float = 0.90,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeSource:
        if isinstance(source_type, str):
            try:
                source_type = KnowledgeSourceType(source_type)
            except ValueError:
                source_type = KnowledgeSourceType.REPOSITORY
        if isinstance(authority, str):
            try:
                authority = KnowledgeSourceAuthority(authority)
            except ValueError:
                authority = KnowledgeSourceAuthority.VERIFIED
        if isinstance(reliability, str):
            try:
                reliability = KnowledgeSourceReliability(reliability)
            except ValueError:
                reliability = KnowledgeSourceReliability.HIGH

        if reliability_score is not None:
            trust_score = reliability_score

        src = KnowledgeSource(
            tenant_id=tenant_id,
            name=name,
            source_type=source_type,
            authority=authority,
            reliability=reliability,
            trust_score=trust_score,
            metadata=metadata or {},
        )
        self._sources[src.source_id] = src
        return src

    def get_source(self, source_id: str, tenant_id: str) -> KnowledgeSource:
        src = self._sources.get(source_id)
        if not src:
            raise KnowledgeSourceNotFoundException(f"Source '{source_id}' not found")
        if src.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return src

    def evaluate_source(self, tenant_id: str, source_id: str) -> Dict[str, Any]:
        src = self.get_source(source_id=source_id, tenant_id=tenant_id)
        return {
            "source_id": src.source_id,
            "authority": src.authority.value,
            "reliability": src.reliability.value,
            "trust_score": src.trust_score,
            "status": src.status.value,
        }

    def list_sources(self, tenant_id: str) -> List[KnowledgeSource]:
        return [s for s in self._sources.values() if s.tenant_id == tenant_id]
