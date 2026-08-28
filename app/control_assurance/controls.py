"""Enterprise Control Registry Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import (
    ControlNotFoundException,
    CrossTenantControlAssuranceAccessException,
)


class ControlType(str, Enum):
    AUTOMATED = "AUTOMATED"
    SEMI_AUTOMATED = "SEMI_AUTOMATED"
    MANUAL = "MANUAL"
    DELEGATED = "DELEGATED"


class ControlCategory(str, Enum):
    SECURITY = "SECURITY"
    DATA = "DATA"
    AI_MODEL = "AI_MODEL"
    AI_AGENT = "AI_AGENT"
    RELIABILITY = "RELIABILITY"
    RESILIENCE = "RESILIENCE"
    COMPLIANCE = "COMPLIANCE"
    IDENTITY = "IDENTITY"
    FINANCIAL = "FINANCIAL"
    OPERATIONAL = "OPERATIONAL"


class ControlCriticality(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ControlStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    DEPRECATED = "DEPRECATED"
    EXEMPTED = "EXEMPTED"


class ControlScope(BaseModel):
    scope_type: str = "SERVICE"
    scope_target: str = "global"
    tenant_id: str = "default"


class ControlOwnerReference(BaseModel):
    owner_id: str
    owner_email: Optional[str] = None
    role: str = "CONTROL_OWNER"


class ControlDefinition(BaseModel):
    code: str
    name: str
    description: str
    category: ControlCategory
    control_type: ControlType = ControlType.AUTOMATED
    criticality: ControlCriticality = ControlCriticality.HIGH
    compliance_requirement_refs: List[str] = Field(default_factory=list)
    governance_policy_refs: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Control(BaseModel):
    control_id: str = Field(default_factory=lambda: f"ctrl_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    definition: ControlDefinition
    status: ControlStatus = ControlStatus.ACTIVE
    scope: ControlScope = Field(default_factory=ControlScope)
    owner: Optional[ControlOwnerReference] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlManager:
    """Manages control definition, registration, and discovery with tenant scoping."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._controls: Dict[str, Control] = {}

    def register_control(
        self,
        tenant_id: str,
        code: str,
        name: str,
        description: str,
        category: ControlCategory,
        control_type: ControlType = ControlType.AUTOMATED,
        criticality: ControlCriticality = ControlCriticality.HIGH,
        compliance_requirement_refs: Optional[List[str]] = None,
        governance_policy_refs: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Control:
        defn = ControlDefinition(
            code=code,
            name=name,
            description=description,
            category=category,
            control_type=control_type,
            criticality=criticality,
            compliance_requirement_refs=compliance_requirement_refs or [],
            governance_policy_refs=governance_policy_refs or [],
            parameters=parameters or {},
        )
        ctrl = Control(
            tenant_id=tenant_id,
            definition=defn,
            scope=ControlScope(tenant_id=tenant_id),
        )
        self._controls[ctrl.control_id] = ctrl
        return ctrl

    def get_control(self, control_id: str, tenant_id: str) -> Control:
        ctrl = self._controls.get(control_id)
        if not ctrl:
            raise ControlNotFoundException(control_id)
        try:
            self.tenant_guard.enforce_isolation(tenant_id, ctrl.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()
        return ctrl

    def list_controls(
        self,
        tenant_id: str,
        category: Optional[ControlCategory] = None,
        status: Optional[ControlStatus] = None,
    ) -> List[Control]:
        res = []
        for ctrl in self._controls.values():
            if ctrl.tenant_id == tenant_id or tenant_id == "global" or ctrl.tenant_id == "global":
                if category and ctrl.definition.category != category:
                    continue
                if status and ctrl.status != status:
                    continue
                res.append(ctrl)
        return res
