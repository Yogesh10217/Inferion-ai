"""Enterprise Identity Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import (
    CrossTenantIdentityAssuranceException,
)


class IdentityType(str, Enum):
    HUMAN = "HUMAN"
    SERVICE = "SERVICE"
    AGENT = "AGENT"
    APPLICATION = "APPLICATION"
    WORKLOAD = "WORKLOAD"
    EXTERNAL = "EXTERNAL"
    API = "API"
    SYSTEM = "SYSTEM"


class IdentityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"
    PENDING = "PENDING"


class IdentityCategory(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    CONTRACTOR = "CONTRACTOR"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    AI_AGENT = "AI_AGENT"
    BOT = "BOT"
    THIRD_PARTY = "THIRD_PARTY"


class IdentityMetadata(BaseModel):
    owner: str = "system"
    department: Optional[str] = None
    environment: str = "production"
    tags: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class IdentityReference(BaseModel):
    identity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    identity_type: IdentityType
    category: IdentityCategory = IdentityCategory.EMPLOYEE
    status: IdentityStatus = IdentityStatus.ACTIVE
    external_id: Optional[str] = None
    metadata: IdentityMetadata = Field(default_factory=IdentityMetadata)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityManager:
    """Manages identity references with strict tenant isolation."""

    def __init__(self) -> None:
        self._identities: Dict[str, IdentityReference] = {}

    def register_identity(
        self,
        tenant_id: str,
        name: str,
        identity_type: IdentityType,
        category: IdentityCategory = IdentityCategory.EMPLOYEE,
        external_id: Optional[str] = None,
        metadata: Optional[IdentityMetadata] = None,
    ) -> IdentityReference:
        identity = IdentityReference(
            tenant_id=tenant_id,
            name=name,
            identity_type=identity_type,
            category=category,
            external_id=external_id,
            metadata=metadata or IdentityMetadata(),
        )
        self._identities[identity.identity_id] = identity
        return identity

    def get_identity(self, tenant_id: str, identity_id: str) -> IdentityReference:
        identity = self._identities.get(identity_id)
        if not identity:
            raise CrossTenantIdentityAssuranceException()
        if identity.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return identity

    def list_identities(
        self,
        tenant_id: str,
        identity_type: Optional[IdentityType] = None,
    ) -> List[IdentityReference]:
        res = []
        for identity in self._identities.values():
            if identity.tenant_id == tenant_id:
                if identity_type is None or identity.identity_type == identity_type:
                    res.append(identity)
        return res
