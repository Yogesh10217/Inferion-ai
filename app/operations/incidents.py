"""Incident Management Lifecycle Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.operations.exceptions import IncidentNotFoundException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentSeverity(str, Enum):
    SEV1_CRITICAL = "SEV1_CRITICAL"
    SEV2_HIGH = "SEV2_HIGH"
    SEV3_MEDIUM = "SEV3_MEDIUM"
    SEV4_LOW = "SEV4_LOW"


class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    POSTMORTEM = "POSTMORTEM"
    CLOSED = "CLOSED"


class TimelineEvent(BaseModel):
    timestamp: datetime = Field(default_factory=_now)
    description: str
    actor: str = "system"


class Incident(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"inc_{uuid.uuid4().hex[:10]}")
    title: str
    tenant_id: str = "global"
    severity: IncidentSeverity = IncidentSeverity.SEV2_HIGH
    status: IncidentStatus = IncidentStatus.DETECTED

    primary_resource_id: Optional[str] = None
    correlated_alert_ids: List[str] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    resolved_at: Optional[datetime] = None


class IncidentManager:
    """Manages multi-tenant incident lifecycles, timeline logging, and alert correlation."""

    def __init__(self) -> None:
        self._incidents: Dict[str, Incident] = {}

    def create_incident(
        self,
        title: str,
        tenant_id: str = "global",
        severity: IncidentSeverity = IncidentSeverity.SEV2_HIGH,
        primary_resource_id: Optional[str] = None,
        alert_ids: Optional[List[str]] = None,
    ) -> Incident:
        inc = Incident(
            title=title,
            tenant_id=tenant_id,
            severity=severity,
            primary_resource_id=primary_resource_id,
            correlated_alert_ids=alert_ids or [],
            timeline=[TimelineEvent(description=f"Incident '{title}' detected and opened.")],
        )
        self._incidents[inc.incident_id] = inc
        logger.warning(f"[INCIDENT MANAGER] Created incident '{inc.incident_id}' ({severity.value}) on tenant '{tenant_id}': {title}")
        return inc

    def update_status(self, incident_id: str, new_status: IncidentStatus, notes: str = "") -> Incident:
        inc = self.get_incident(incident_id)
        old_status = inc.status
        inc.status = new_status
        inc.updated_at = _now()

        if new_status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED) and not inc.resolved_at:
            inc.resolved_at = _now()

        msg = f"Status changed from {old_status.value} to {new_status.value}."
        if notes:
            msg += f" Notes: {notes}"
        inc.timeline.append(TimelineEvent(description=msg))

        logger.info(f"[INCIDENT MANAGER] Updated incident '{incident_id}' status -> {new_status.value}")
        return inc

    def get_incident(self, incident_id: str) -> Incident:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise IncidentNotFoundException(incident_id)
        return inc

    def list_incidents(self, tenant_id: Optional[str] = None, status: Optional[IncidentStatus] = None) -> List[Incident]:
        res = list(self._incidents.values())
        if tenant_id:
            res = [i for i in res if i.tenant_id == tenant_id]
        if status:
            res = [i for i in res if i.status == status]
        return res
