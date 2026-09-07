"""Operational incident lifecycle state machine and manager."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, OperationalIncidentNotFoundException


class OperationalIncidentState(str, Enum):
    DETECTED = "DETECTED"
    ANALYZING = "ANALYZING"
    INVESTIGATING = "INVESTIGATING"
    MITIGATION_PLANNED = "MITIGATION_PLANNED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    DELEGATED = "DELEGATED"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class OperationalIncidentSeverity(str, Enum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"


class OperationalIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    title: str
    severity: OperationalIncidentSeverity = OperationalIncidentSeverity.SEV2
    state: OperationalIncidentState = OperationalIncidentState.DETECTED
    summary: str = ""
    assigned_team: str = "operations"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalIncidentManager:
    """Manages the operational incident lifecycle following delegation and governance rules."""

    def __init__(self) -> None:
        self._incidents: Dict[str, Dict[str, OperationalIncident]] = {}  # tenant_id -> {incident_id: inc}

    def create_incident(
        self,
        tenant_id: str,
        service_id: str,
        title: str,
        severity: OperationalIncidentSeverity = OperationalIncidentSeverity.SEV2,
        summary: str = "",
    ) -> OperationalIncident:
        inc = OperationalIncident(
            tenant_id=tenant_id,
            service_id=service_id,
            title=title,
            severity=severity,
            state=OperationalIncidentState.DETECTED,
            summary=summary,
        )
        if tenant_id not in self._incidents:
            self._incidents[tenant_id] = {}
        self._incidents[tenant_id][inc.incident_id] = inc
        return inc

    def transition_state(
        self,
        tenant_id: str,
        incident_id: str,
        new_state: OperationalIncidentState,
    ) -> OperationalIncident:
        inc = self.get_incident(tenant_id, incident_id)
        inc.state = new_state
        inc.updated_at = datetime.now(timezone.utc)
        return inc

    def get_incident(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        if tenant_id not in self._incidents or incident_id not in self._incidents[tenant_id]:
            for tid, incs in self._incidents.items():
                if tid != tenant_id and incident_id in incs:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise OperationalIncidentNotFoundException("Operational incident not found.")
        return self._incidents[tenant_id][incident_id]

    def list_incidents(self, tenant_id: str, service_id: Optional[str] = None) -> List[OperationalIncident]:
        tenant_incs = self._incidents.get(tenant_id, {})
        if service_id:
            return [i for i in tenant_incs.values() if i.service_id == service_id]
        return list(tenant_incs.values())
