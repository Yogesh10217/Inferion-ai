"""Identity-Access Relationship Intelligence (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class AccessRelationshipType(str, Enum):
    ASSIGNED_ROLE = "ASSIGNED_ROLE"
    GRANTED_PERMISSION = "GRANTED_PERMISSION"
    AGENT_TOOL_ACCESS = "AGENT_TOOL_ACCESS"
    SERVICE_RESOURCE_ACCESS = "SERVICE_RESOURCE_ACCESS"
    IDENTITY_DATASET_ACCESS = "IDENTITY_DATASET_ACCESS"
    AGENT_KNOWLEDGE_ACCESS = "AGENT_KNOWLEDGE_ACCESS"


class RelationshipStrength(str, Enum):
    DIRECT = "DIRECT"
    INHERITED = "INHERITED"
    TEMPORARY = "TEMPORARY"
    DELEGATED = "DELEGATED"


class RelationshipStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class AccessRelationship(BaseModel):
    """Identity-Access Relationship representation."""

    relationship_id: str = Field(default_factory=lambda: f"rel_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source_identity_id: str
    target_resource_id: str
    relationship_type: AccessRelationshipType
    strength: RelationshipStrength = RelationshipStrength.DIRECT
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    entitlement_id: Optional[str] = None
    is_active: bool = True
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessRelationshipManager:
    """Manages identity-to-resource access relationships."""

    def __init__(self) -> None:
        self._relationships: Dict[str, AccessRelationship] = {}

    def create_relationship(
        self,
        tenant_id: str,
        source_identity_id: str,
        target_resource_id: str,
        relationship_type: AccessRelationshipType,
        strength: RelationshipStrength = RelationshipStrength.DIRECT,
        entitlement_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessRelationship:
        rel = AccessRelationship(
            tenant_id=tenant_id,
            source_identity_id=source_identity_id,
            target_resource_id=target_resource_id,
            relationship_type=relationship_type,
            strength=strength,
            entitlement_id=entitlement_id,
            expires_at=expires_at,
            metadata=metadata or {},
        )
        self._relationships[rel.relationship_id] = rel
        return rel

    def get_relationship(self, tenant_id: str, relationship_id: str) -> AccessRelationship:
        rel = self._relationships.get(relationship_id)
        if not rel or rel.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return rel

    def list_relationships(
        self,
        tenant_id: str,
        source_identity_id: Optional[str] = None,
        target_resource_id: Optional[str] = None,
        relationship_type: Optional[AccessRelationshipType] = None,
    ) -> List[AccessRelationship]:
        results = [r for r in self._relationships.values() if r.tenant_id == tenant_id]
        if source_identity_id:
            results = [r for r in results if r.source_identity_id == source_identity_id]
        if target_resource_id:
            results = [r for r in results if r.target_resource_id == target_resource_id]
        if relationship_type:
            results = [r for r in results if r.relationship_type == relationship_type]
        return results

    def revoke_relationship(self, tenant_id: str, relationship_id: str) -> AccessRelationship:
        rel = self.get_relationship(tenant_id, relationship_id)
        rel.status = RelationshipStatus.REVOKED
        rel.is_active = False
        return rel
