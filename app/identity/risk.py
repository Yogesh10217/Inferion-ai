"""Identity Behavioral Risk Detection & Anomaly Intelligence Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations.incidents import IncidentManager, IncidentSeverity

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AnomalyType(str, Enum):
    IMPOSSIBLE_TRAVEL = "IMPOSSIBLE_TRAVEL"
    UNUSUAL_IP = "UNUSUAL_IP"
    UNUSUAL_DEVICE = "UNUSUAL_DEVICE"
    EXCESSIVE_FAILED_AUTH = "EXCESSIVE_FAILED_AUTH"
    TOKEN_ABUSE = "TOKEN_ABUSE"
    API_ABUSE = "API_ABUSE"
    PRIVILEGE_ESCALATION_ATTEMPT = "PRIVILEGE_ESCALATION_ATTEMPT"
    SUSPICIOUS_AUTOMATION = "SUSPICIOUS_AUTOMATION"
    UNUSUAL_DATA_ACCESS = "UNUSUAL_DATA_ACCESS"
    UNUSUAL_AGENT_ACTIVITY = "UNUSUAL_AGENT_ACTIVITY"


class IdentityRiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IdentityRiskEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"id_risk_{uuid.uuid4().hex[:10]}")
    identity_id: str
    tenant_id: str = "global"
    anomaly_type: AnomalyType = AnomalyType.UNUSUAL_IP
    severity: IdentityRiskSeverity = IdentityRiskSeverity.MEDIUM

    description: str = ""
    ip_address: str = "127.0.0.1"
    incident_id: Optional[str] = None
    detected_at: datetime = Field(default_factory=_now)


class IdentityRiskEngine:
    """Detects behavioral anomalies and automatically creates Operations Incidents for HIGH/CRITICAL events."""

    def __init__(self, incident_manager: Optional[IncidentManager] = None) -> None:
        self.incident_manager = incident_manager or IncidentManager()
        self._risk_events: Dict[str, IdentityRiskEvent] = {}

    def record_risk_event(
        self,
        identity_id: str,
        anomaly_type: AnomalyType,
        severity: IdentityRiskSeverity,
        description: str = "",
        tenant_id: str = "global",
        ip_address: str = "127.0.0.1",
    ) -> IdentityRiskEvent:
        evt = IdentityRiskEvent(
            identity_id=identity_id,
            anomaly_type=anomaly_type,
            severity=severity,
            description=description,
            tenant_id=tenant_id,
            ip_address=ip_address,
        )

        # For HIGH or CRITICAL severity, automatically trigger an Operations Incident
        if severity in (IdentityRiskSeverity.CRITICAL, IdentityRiskSeverity.HIGH):
            op_sev = IncidentSeverity.SEV1_CRITICAL if severity == IdentityRiskSeverity.CRITICAL else IncidentSeverity.SEV2_HIGH
            inc = self.incident_manager.create_incident(
                title=f"[IDENTITY RISK] {anomaly_type.value} for '{identity_id}'",
                tenant_id=tenant_id,
                severity=op_sev,
                primary_resource_id=identity_id,
            )
            evt.incident_id = inc.incident_id
            logger.warning(f"[IDENTITY RISK ENGINE] Created Operations Incident '{inc.incident_id}' for {severity.value} identity risk event '{evt.event_id}'")

        self._risk_events[evt.event_id] = evt
        logger.info(f"[IDENTITY RISK ENGINE] Recorded risk event '{evt.event_id}' ({anomaly_type.value}) for '{identity_id}'")
        return evt

    def get_event(self, event_id: str) -> IdentityRiskEvent:
        evt = self._risk_events.get(event_id)
        if not evt:
            raise KeyError(f"Identity risk event '{event_id}' not found")
        return evt

    def list_events(self, tenant_id: Optional[str] = None) -> List[IdentityRiskEvent]:
        res = list(self._risk_events.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
