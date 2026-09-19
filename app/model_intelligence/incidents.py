"""Model Incident Governance Lifecycle (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import (
    CrossTenantModelIntelligenceException,
    ImmutableModelIntelligenceRecordException,
    ModelIncidentNotFoundException,
)

logger = logging.getLogger(__name__)


class ModelIncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ModelIncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class ModelIncidentImpact(BaseModel):
    affected_services: List[str] = Field(default_factory=list)
    affected_users_count: int = 0
    estimated_financial_loss: float = 0.0
    sla_breached: bool = False


class ModelIncident(BaseModel):
    incident_id: str
    model_id: str
    tenant_id: str
    title: str
    severity: ModelIncidentSeverity
    status: ModelIncidentStatus = ModelIncidentStatus.DETECTED
    impact: ModelIncidentImpact
    remediation_plan_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None


class ModelIncidentManager:
    """Manages model incident governance lifecycle."""

    def __init__(self) -> None:
        self._incidents: Dict[str, ModelIncident] = {}

    def create_incident(
        self,
        model_id: str,
        tenant_id: str,
        title: str,
        severity: ModelIncidentSeverity,
        impact: Optional[ModelIncidentImpact] = None,
    ) -> ModelIncident:
        inc_id = f"minc-{uuid.uuid4().hex[:8]}"
        incident = ModelIncident(
            incident_id=inc_id,
            model_id=model_id,
            tenant_id=tenant_id,
            title=title,
            severity=severity,
            impact=impact or ModelIncidentImpact(),
        )
        self._incidents[inc_id] = incident
        logger.info(
            f"[MODEL INCIDENT] Created incident {inc_id} for model {model_id} (Tenant: {tenant_id}) Severity: {severity}"
        )
        return incident

    def update_status(
        self,
        incident_id: str,
        tenant_id: str,
        new_status: ModelIncidentStatus,
    ) -> ModelIncident:
        inc = self.get_incident(incident_id, tenant_id)
        if inc.status == ModelIncidentStatus.CLOSED:
            raise ImmutableModelIntelligenceRecordException(f"Incident '{incident_id}' is closed and immutable.")

        inc.status = new_status
        inc.updated_at = datetime.now(timezone.utc)
        if new_status == ModelIncidentStatus.CLOSED:
            inc.closed_at = datetime.now(timezone.utc)

        logger.info(f"[MODEL INCIDENT] Updated incident {incident_id} status to {new_status}")
        return inc

    def get_incident(self, incident_id: str, tenant_id: str) -> ModelIncident:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise ModelIncidentNotFoundException(f"Incident '{incident_id}' not found.")
        if inc.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return inc

    def list_incidents(self, tenant_id: str, model_id: Optional[str] = None) -> List[ModelIncident]:
        res = [i for i in self._incidents.values() if i.tenant_id == tenant_id]
        if model_id:
            res = [i for i in res if i.model_id == model_id]
        return res
