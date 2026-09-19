"""Enterprise Compliance Control Management System."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import (
    ControlNotFoundException,
    CrossTenantComplianceAccessException,
)


class ControlType(str, Enum):
    PREVENTIVE = "PREVENTIVE"
    DETECTIVE = "DETECTIVE"
    CORRECTIVE = "CORRECTIVE"
    COMPENSATING = "COMPENSATING"


class ControlCategory(str, Enum):
    IDENTITY = "IDENTITY"
    ACCESS = "ACCESS"
    SECURITY = "SECURITY"
    DATA = "DATA"
    PRIVACY = "PRIVACY"
    MODEL = "MODEL"
    AGENT = "AGENT"
    ARCHITECTURE = "ARCHITECTURE"
    OPERATIONS = "OPERATIONS"
    CHANGE_MANAGEMENT = "CHANGE_MANAGEMENT"
    OBSERVABILITY = "OBSERVABILITY"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    BUSINESS_CONTINUITY = "BUSINESS_CONTINUITY"
    GOVERNANCE = "GOVERNANCE"
    FINOPS = "FINOPS"


class ControlStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    INACTIVE = "INACTIVE"


class ControlFrequency(str, Enum):
    CONTINUOUS = "CONTINUOUS"
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    ON_DEMAND = "ON_DEMAND"


class ControlCriticality(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ControlImplementation(BaseModel):
    implementation_id: str = Field(default_factory=lambda: f"impl_{uuid.uuid4().hex[:12]}")
    source_subsystem: str  # e.g., DataGovernanceManager, IdentitySecurityManager
    method_name: str
    is_automated: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ControlObjective(BaseModel):
    objective_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str


class ComplianceControl(BaseModel):
    control_id: str = Field(default_factory=lambda: f"ctrl_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    code: str  # e.g., CTRL-SEC-01
    name: str
    description: str
    control_type: ControlType = ControlType.PREVENTIVE
    category: ControlCategory = ControlCategory.SECURITY
    status: ControlStatus = ControlStatus.ACTIVE
    frequency: ControlFrequency = ControlFrequency.CONTINUOUS
    criticality: ControlCriticality = ControlCriticality.HIGH
    implementation: ControlImplementation
    requirement_ids: List[str] = Field(default_factory=list)
    owner_id: str = "security_admin"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlManager:
    """Manages enterprise compliance controls and their implementation references."""

    def __init__(self) -> None:
        self._controls: Dict[str, ComplianceControl] = {}

    def register_control(
        self,
        tenant_id: str,
        code: str,
        name: str,
        description: str,
        control_type: ControlType,
        category: ControlCategory,
        implementation: ControlImplementation,
        requirement_ids: Optional[List[str]] = None,
        criticality: ControlCriticality = ControlCriticality.HIGH,
    ) -> ComplianceControl:
        ctrl = ComplianceControl(
            tenant_id=tenant_id,
            code=code,
            name=name,
            description=description,
            control_type=control_type,
            category=category,
            implementation=implementation,
            requirement_ids=requirement_ids or [],
            criticality=criticality,
        )
        self._controls[ctrl.control_id] = ctrl
        return ctrl

    def get_control(self, control_id: str, tenant_id: str) -> ComplianceControl:
        ctrl = self._controls.get(control_id)
        if not ctrl:
            raise ControlNotFoundException(control_id=control_id, tenant_id=tenant_id)
        if ctrl.tenant_id != tenant_id and tenant_id != "global" and ctrl.tenant_id != "global":
            raise CrossTenantComplianceAccessException(
                request_tenant=tenant_id, target_tenant=ctrl.tenant_id, resource_id=control_id
            )
        return ctrl

    def list_controls(self, tenant_id: str, category: Optional[ControlCategory] = None) -> List[ComplianceControl]:
        ctrls = [c for c in self._controls.values() if c.tenant_id in (tenant_id, "global")]
        if category:
            ctrls = [c for c in ctrls if c.category == category]
        return ctrls

    def update_control_status(self, control_id: str, tenant_id: str, status: ControlStatus) -> ComplianceControl:
        ctrl = self.get_control(control_id, tenant_id)
        ctrl.status = status
        return ctrl
