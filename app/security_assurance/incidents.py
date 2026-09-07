"""Security Incident Management & Lifecycle Engine."""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_assurance.exceptions import SecurityIncidentNotFoundException, CrossTenantSecurityAssuranceException


class SecurityIncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityIncidentState(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    CONTAINED = "CONTAINED"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"


class SecurityIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"sec-inc-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    title: str
    severity: SecurityIncidentSeverity
    state: SecurityIncidentState = SecurityIncidentState.OPEN
    threat_ids: List[str] = Field(default_factory=list)
    affected_asset_ids: List[str] = Field(default_factory=list)
    idempotency_key: Optional[str] = None
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityIncidentManager:
    """Manages creation, tracking, state transitions, and idempotency for security incidents."""

    def __init__(self) -> None:
        self._incidents: Dict[str, SecurityIncident] = {}
        self._idempotency_map: Dict[str, str] = {}  # idempotency_key -> incident_id

    def create_incident(
        self,
        tenant_id: str,
        title: str,
        severity: SecurityIncidentSeverity,
        threat_ids: Optional[List[str]] = None,
        affected_asset_ids: Optional[List[str]] = None,
        description: str = "",
        idempotency_key: Optional[str] = None,
    ) -> SecurityIncident:
        if idempotency_key and idempotency_key in self._idempotency_map:
            existing_id = self._idempotency_map[idempotency_key]
            return self.get_incident(tenant_id, existing_id)

        incident = SecurityIncident(
            tenant_id=tenant_id,
            title=title,
            severity=severity,
            threat_ids=threat_ids or [],
            affected_asset_ids=affected_asset_ids or [],
            description=description,
            idempotency_key=idempotency_key,
        )
        self._incidents[incident.incident_id] = incident
        if idempotency_key:
            self._idempotency_map[idempotency_key] = incident.incident_id
        return incident

    def get_incident(self, tenant_id: str, incident_id: str) -> SecurityIncident:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise SecurityIncidentNotFoundException(f"Security incident '{incident_id}' not found.")
        if inc.tenant_id != tenant_id:
            raise CrossTenantSecurityAssuranceException(f"Tenant '{tenant_id}' cannot access incident for tenant '{inc.tenant_id}'.")
        return inc

    def update_incident_state(self, tenant_id: str, incident_id: str, state: SecurityIncidentState) -> SecurityIncident:
        inc = self.get_incident(tenant_id, incident_id)
        inc.state = state
        inc.updated_at = datetime.now(timezone.utc)
        return inc

    def list_incidents(self, tenant_id: str, state: Optional[SecurityIncidentState] = None) -> List[SecurityIncident]:
        results = [i for i in self._incidents.values() if i.tenant_id == tenant_id]
        if state:
            results = [i for i in results if i.state == state]
        return results
