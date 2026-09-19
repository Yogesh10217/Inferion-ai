"""Enterprise Entitlement Intelligence (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class EntitlementType(str, Enum):
    PERMISSION = "PERMISSION"
    ROLE = "ROLE"
    SCOPE = "SCOPE"
    POLICY_BINDING = "POLICY_BINDING"
    ACTION_GRANT = "ACTION_GRANT"


class EntitlementScope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"
    WORKSPACE = "WORKSPACE"
    RESOURCE = "RESOURCE"


class EntitlementCriticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EntitlementStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class EntitlementReference(BaseModel):
    """Reference pointing to IAM entitlement without direct mutation."""

    external_entitlement_id: str
    target_resource_type: str
    target_resource_id: str
    action_type: str


class Entitlement(BaseModel):
    """Enterprise Entitlement Representation."""

    entitlement_id: str = Field(default_factory=lambda: f"ent_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    code: str
    name: str
    description: str = ""
    entitlement_type: EntitlementType
    scope: EntitlementScope = EntitlementScope.TENANT
    criticality: EntitlementCriticality = EntitlementCriticality.MEDIUM
    status: EntitlementStatus = EntitlementStatus.ACTIVE
    reference: EntitlementReference
    is_privileged: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntitlementManager:
    """Manages entitlement definitions and catalog without direct enforcement."""

    def __init__(self) -> None:
        self._entitlements: Dict[str, Entitlement] = {}

    def register_entitlement(
        self,
        tenant_id: str,
        code: str,
        name: str,
        entitlement_type: EntitlementType,
        external_entitlement_id: str,
        target_resource_type: str,
        target_resource_id: str,
        action_type: str,
        scope: EntitlementScope = EntitlementScope.TENANT,
        criticality: EntitlementCriticality = EntitlementCriticality.MEDIUM,
        is_privileged: bool = False,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entitlement:
        ref = EntitlementReference(
            external_entitlement_id=external_entitlement_id,
            target_resource_type=target_resource_type,
            target_resource_id=target_resource_id,
            action_type=action_type,
        )
        ent = Entitlement(
            tenant_id=tenant_id,
            code=code,
            name=name,
            description=description,
            entitlement_type=entitlement_type,
            scope=scope,
            criticality=criticality,
            is_privileged=is_privileged,
            reference=ref,
            metadata=metadata or {},
        )
        self._entitlements[ent.entitlement_id] = ent
        return ent

    def get_entitlement(self, tenant_id: str, entitlement_id: str) -> Entitlement:
        ent = self._entitlements.get(entitlement_id)
        if not ent or ent.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return ent

    def list_entitlements(
        self,
        tenant_id: str,
        entitlement_type: Optional[EntitlementType] = None,
        is_privileged: Optional[bool] = None,
    ) -> List[Entitlement]:
        results = [e for e in self._entitlements.values() if e.tenant_id == tenant_id]
        if entitlement_type:
            results = [e for e in results if e.entitlement_type == entitlement_type]
        if is_privileged is not None:
            results = [e for e in results if e.is_privileged == is_privileged]
        return results
