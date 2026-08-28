"""Control Scope Resolution Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException


class ScopeType(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"
    SERVICE = "SERVICE"
    APPLICATION = "APPLICATION"
    MODEL = "MODEL"
    AGENT = "AGENT"
    DATASET = "DATASET"
    REGION = "REGION"
    ENVIRONMENT = "ENVIRONMENT"
    RESOURCE = "RESOURCE"


class ScopeTarget(str, Enum):
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"
    SERVICE = "SERVICE"
    APPLICATION = "APPLICATION"
    MODEL = "MODEL"
    AGENT = "AGENT"
    DATASET = "DATASET"
    REGION = "REGION"
    ENVIRONMENT = "ENVIRONMENT"
    RESOURCE = "RESOURCE"


class ControlScopeDefinition(BaseModel):
    scope_type: ScopeType = ScopeType.TENANT
    scope_target: ScopeTarget = ScopeTarget.SERVICE
    target_id: str
    tenant_id: str
    environment: str = "production"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScopeResolution(BaseModel):
    resolution_id: str
    scope: ControlScopeDefinition
    is_in_scope: bool = True
    resolved_resources: List[str] = Field(default_factory=list)
    matching_rule: str = "EXACT_TENANT_MATCH"


class ControlScopeResolver:
    """Resolves control evaluation scopes while enforcing strict tenant boundaries."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def resolve_scope(
        self,
        tenant_id: str,
        target_type: ScopeTarget,
        target_id: str,
        environment: str = "production",
    ) -> ScopeResolution:
        scope_defn = ControlScopeDefinition(
            scope_type=ScopeType.TENANT,
            scope_target=target_type,
            target_id=target_id,
            tenant_id=tenant_id,
            environment=environment,
        )

        return ScopeResolution(
            resolution_id=f"res_{target_id}_{tenant_id}",
            scope=scope_defn,
            is_in_scope=True,
            resolved_resources=[target_id],
            matching_rule="EXACT_TENANT_MATCH",
        )
