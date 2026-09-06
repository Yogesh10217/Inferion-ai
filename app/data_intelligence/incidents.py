"""Data incident lifecycle management (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import DataIncidentNotFoundException, CrossTenantDataIntelligenceException


class DataIncidentSeverity(str, Enum):
    P4_LOW = "P4_LOW"
    P3_MEDIUM = "P3_MEDIUM"
    P2_HIGH = "P2_HIGH"
    P1_CRITICAL = "P1_CRITICAL"


class DataIncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class DataIncident(BaseModel):
    incident_id: str
    dataset_id: str
    tenant_id: str
    title: str
    severity: DataIncidentSeverity
    status: DataIncidentStatus = DataIncidentStatus.DETECTED
    anomaly_id: Optional[str] = None
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


class DataIncidentManager:
    """Manages full lifecycle of data incidents."""

    def __init__(self) -> None:
        self._incidents: Dict[str, DataIncident] = {}

    def create_incident(
        self,
        dataset_id: str,
        tenant_id: str,
        title: str,
        severity: DataIncidentSeverity,
        anomaly_id: Optional[str] = None,
        description: str = "",
        incident_id: Optional[str] = None,
    ) -> DataIncident:
        iid = incident_id or f"dinc-{uuid.uuid4().hex[:8]}"
        inc = DataIncident(
            incident_id=iid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            title=title,
            severity=severity,
            status=DataIncidentStatus.DETECTED,
            anomaly_id=anomaly_id,
            description=description,
        )
        self._incidents[iid] = inc
        return inc

    def get_incident(self, incident_id: str, tenant_id: str) -> DataIncident:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise DataIncidentNotFoundException(incident_id)
        if inc.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return inc

    def update_status(self, incident_id: str, tenant_id: str, status: DataIncidentStatus) -> DataIncident:
        inc = self.get_incident(incident_id, tenant_id)
        inc.status = status
        if status in (DataIncidentStatus.RESOLVED, DataIncidentStatus.CLOSED):
            inc.resolved_at = datetime.now(timezone.utc)
        return inc

    def list_incidents(self, tenant_id: str, dataset_id: Optional[str] = None) -> List[DataIncident]:
        incs = [i for i in self._incidents.values() if i.tenant_id == tenant_id]
        if dataset_id:
            incs = [i for i in incs if i.dataset_id == dataset_id]
        return incs
