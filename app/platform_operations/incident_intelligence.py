"""Incident Intelligence & Enrichment Engine."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations.incidents import Incident, IncidentManager, IncidentSeverity, TimelineEvent
from app.platform_operations.anomalies import Anomaly
from app.platform_operations.impact import ImpactAssessment
from app.platform_operations.signals import OperationalSignal

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentCorrelation(BaseModel):
    correlation_id: str
    incident_id: str
    tenant_id: str
    correlated_signal_ids: List[str] = Field(default_factory=list)
    correlated_anomaly_ids: List[str] = Field(default_factory=list)
    correlated_deployment_ids: List[str] = Field(default_factory=list)
    correlated_governance_event_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class IncidentContext(BaseModel):
    incident_id: str
    tenant_id: str
    incident: Incident
    impact: Optional[ImpactAssessment] = None
    signals: List[OperationalSignal] = Field(default_factory=list)
    anomalies: List[Anomaly] = Field(default_factory=list)
    recent_deployments: List[Dict[str, Any]] = Field(default_factory=list)
    recent_cost_anomalies: List[Dict[str, Any]] = Field(default_factory=list)


class IncidentIntelligenceEngine:
    """Enriches operational incidents with multi-dimensional context without duplicating Incident storage."""

    def __init__(self, incident_manager: Optional[IncidentManager] = None) -> None:
        self.incident_manager = incident_manager or IncidentManager()
        self._contexts: Dict[str, IncidentContext] = {}

    def create_and_enrich_incident(
        self,
        tenant_id: str,
        title: str,
        severity: IncidentSeverity = IncidentSeverity.SEV2_HIGH,
        primary_resource_id: Optional[str] = None,
        impact: Optional[ImpactAssessment] = None,
        signals: Optional[List[OperationalSignal]] = None,
        anomalies: Optional[List[Anomaly]] = None,
        recent_deployments: Optional[List[Dict[str, Any]]] = None,
    ) -> IncidentContext:
        # Create underlying Incident in app.operations
        inc = self.incident_manager.create_incident(
            tenant_id=tenant_id,
            title=title,
            severity=severity,
            primary_resource_id=primary_resource_id,
        )

        # Log timeline event
        inc.timeline.append(
            TimelineEvent(
                description=f"Incident intelligence context constructed with {len(signals or [])} signals and {len(anomalies or [])} anomalies.",
                actor="IncidentIntelligenceEngine",
            )
        )

        context = IncidentContext(
            incident_id=inc.incident_id,
            tenant_id=tenant_id,
            incident=inc,
            impact=impact,
            signals=signals or [],
            anomalies=anomalies or [],
            recent_deployments=recent_deployments or [],
        )
        self._contexts[inc.incident_id] = context
        logger.info(f"[INCIDENT INTELLIGENCE] Created & enriched incident '{inc.incident_id}' for tenant '{tenant_id}'")
        return context

    def get_incident_context(self, incident_id: str, tenant_id: str) -> IncidentContext:
        if incident_id not in self._contexts:
            # Fallback construct basic context from IncidentManager
            inc = self.incident_manager.get_incident(incident_id)
            if inc.tenant_id not in (tenant_id, "global"):
                raise ValueError(f"Incident '{incident_id}' not accessible by tenant '{tenant_id}'.")
            return IncidentContext(incident_id=inc.incident_id, tenant_id=tenant_id, incident=inc)

        ctx = self._contexts[incident_id]
        if ctx.tenant_id not in (tenant_id, "global"):
            raise ValueError(f"Incident '{incident_id}' not accessible by tenant '{tenant_id}'.")
        return ctx
