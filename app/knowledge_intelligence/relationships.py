"""Knowledge Relationship Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeRelationshipNotFoundException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


class RelationshipType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    DERIVED_FROM = "DERIVED_FROM"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    RELATED_TO = "RELATED_TO"
    CAUSES = "CAUSES"
    AFFECTS = "AFFECTS"
    GOVERNS = "GOVERNS"
    REPLACES = "REPLACES"
    SUPERSEDES = "SUPERSEDES"
    IMPLEMENTS = "IMPLEMENTS"
    OBSERVED_IN = "OBSERVED_IN"


class RelationshipStrength(str, Enum):
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    DEFINITIVE = "DEFINITIVE"


class RelationshipDirection(str, Enum):
    DIRECTED = "DIRECTED"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class RelationshipEvidence(BaseModel):
    evidence_id: str
    description: str
    confidence: float = 1.0


class KnowledgeRelationship(BaseModel):
    relationship_id: str = Field(default_factory=lambda: f"krel_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: RelationshipStrength = RelationshipStrength.STRONG
    direction: RelationshipDirection = RelationshipDirection.DIRECTED
    evidence: List[RelationshipEvidence] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeRelationshipManager:
    """Manages cross-knowledge entity relationships and evidence links with tenant isolation."""

    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeRelationship] = {}

    def create_relationship(
        self,
        tenant_id: str,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType = RelationshipType.RELATED_TO,
        strength: RelationshipStrength = RelationshipStrength.STRONG,
        evidence_description: str = "Explicit relationship creation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeRelationship:
        sanitized_meta = SensitiveDataSanitizer.sanitize(metadata or {})
        ev = RelationshipEvidence(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            description=evidence_description,
        )
        rel = KnowledgeRelationship(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength,
            evidence=[ev],
            metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
        )
        self._store[rel.relationship_id] = rel
        return rel

    def get_relationship(self, relationship_id: str, tenant_id: str) -> KnowledgeRelationship:
        rel = self._store.get(relationship_id)
        if not rel:
            raise KnowledgeRelationshipNotFoundException(relationship_id)
        if rel.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAccessException(tenant_id)
        return rel

    def list_relationships(
        self,
        tenant_id: str,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> List[KnowledgeRelationship]:
        results = [r for r in self._store.values() if r.tenant_id == tenant_id]
        if source_id:
            results = [r for r in results if r.source_id == source_id]
        if target_id:
            results = [r for r in results if r.target_id == target_id]
        return results
