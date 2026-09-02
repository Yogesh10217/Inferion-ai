"""Enterprise Incident Lifecycle Management (Phase 5.41)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import (
    CrossTenantOperationsAccessException,
    InvalidAccessStateTransitionException,
)


class IncidentSeverity(str, Enum):
    P1_CRITICAL = "P1_CRITICAL"
    P2_HIGH = "P2_HIGH"
    P3_MEDIUM = "P3_MEDIUM"
    P4_LOW = "P4_LOW"


class IncidentPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class OperationalIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"inc_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    affected_service_id: str
    severity: IncidentSeverity = IncidentSeverity.P2_HIGH
    priority: IncidentPriority = IncidentPriority.P2
    status: IncidentStatus = IncidentStatus.DETECTED
    external_itsm_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class IncidentManager:
    """Manages operational incident lifecycle."""

    def __init__(self) -> None:
        self._incidents: Dict[str, OperationalIncident] = {}

    def create_incident(
        self,
        tenant_id: str,
        title: str,
        affected_service_id: str,
        severity: IncidentSeverity = IncidentSeverity.P2_HIGH,
        priority: IncidentPriority = IncidentPriority.P2,
        external_itsm_ref: Optional[str] = None,
    ) -> OperationalIncident:
        inc = OperationalIncident(
            tenant_id=tenant_id,
            title=title,
            affected_service_id=affected_service_id,
            severity=severity,
            priority=priority,
            external_itsm_ref=external_itsm_ref,
        )
        self._incidents[inc.incident_id] = inc
        return inc

    def acknowledge_incident(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        inc = self.get_incident(tenant_id, incident_id)
        if inc.status != IncidentStatus.DETECTED:
            raise InvalidAccessStateTransitionException(inc.status.value, IncidentStatus.ACKNOWLEDGED.value)
        inc.status = IncidentStatus.ACKNOWLEDGED
        return inc

    def start_investigating(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        inc = self.get_incident(tenant_id, incident_id)
        inc.status = IncidentStatus.INVESTIGATING
        return inc

    def set_mitigating(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        inc = self.get_incident(tenant_id, incident_id)
        inc.status = IncidentStatus.MITIGATING
        return inc

    def resolve_incident(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        inc = self.get_incident(tenant_id, incident_id)
        inc.status = IncidentStatus.RESOLVED
        inc.resolved_at = datetime.now(timezone.utc)
        return inc

    def close_incident(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        inc = self.get_incident(tenant_id, incident_id)
        inc.status = IncidentStatus.CLOSED
        inc.closed_at = datetime.now(timezone.utc)
        return inc

    def get_incident(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        inc = self._incidents.get(incident_id)
        if not inc or inc.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return inc

    def list_incidents(self, tenant_id: str) -> List[OperationalIncident]:
        return [i for i in self._incidents.values() if i.tenant_id == tenant_id]
