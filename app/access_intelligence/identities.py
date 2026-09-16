"""Enterprise Identity Intelligence Registry (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class IdentityType(str, Enum):
    HUMAN_USER = "HUMAN_USER"
    SERVICE_IDENTITY = "SERVICE_IDENTITY"
    AGENT = "AGENT"
    APPLICATION = "APPLICATION"
    WORKLOAD = "WORKLOAD"


class IdentityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"
    REVOKED = "REVOKED"


class IdentityRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IdentityReference(BaseModel):
    """Reference pointing to existing identity resource in app.identity / external IAM."""
    external_id: str
    identity_type: IdentityType
    provider: str = "internal"
    attributes: Dict[str, Any] = Field(default_factory=dict)


class AccessIdentity(BaseModel):
    """Access Intelligence Identity Representation."""
    identity_id: str = Field(default_factory=lambda: f"ident_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    identity_type: IdentityType
    status: IdentityStatus = IdentityStatus.ACTIVE
    risk_level: IdentityRiskLevel = IdentityRiskLevel.LOW
    reference: IdentityReference
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IdentityManager:
    """Manages identity references for Access Intelligence without duplicating storage."""

    def __init__(self) -> None:
        self._identities: Dict[str, AccessIdentity] = {}

    def register_identity(
        self,
        tenant_id: str,
        name: str,
        identity_type: IdentityType,
        external_id: str,
        provider: str = "internal",
        risk_level: IdentityRiskLevel = IdentityRiskLevel.LOW,
        tags: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessIdentity:
        ref = IdentityReference(
            external_id=external_id,
            identity_type=identity_type,
            provider=provider,
            attributes=attributes or {},
        )
        ident = AccessIdentity(
            tenant_id=tenant_id,
            name=name,
            identity_type=identity_type,
            risk_level=risk_level,
            reference=ref,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._identities[ident.identity_id] = ident
        return ident

    def get_identity(self, tenant_id: str, identity_id: str) -> AccessIdentity:
        ident = self._identities.get(identity_id)
        if not ident or ident.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return ident

    def list_identities(
        self,
        tenant_id: str,
        identity_type: Optional[IdentityType] = None,
        risk_level: Optional[IdentityRiskLevel] = None,
    ) -> List[AccessIdentity]:
        results = [i for i in self._identities.values() if i.tenant_id == tenant_id]
        if identity_type:
            results = [i for i in results if i.identity_type == identity_type]
        if risk_level:
            results = [i for i in results if i.risk_level == risk_level]
        return results

    def update_identity_risk(self, tenant_id: str, identity_id: str, risk_level: IdentityRiskLevel) -> AccessIdentity:
        ident = self.get_identity(tenant_id, identity_id)
        ident.risk_level = risk_level
        ident.updated_at = datetime.now(timezone.utc)
        return ident
