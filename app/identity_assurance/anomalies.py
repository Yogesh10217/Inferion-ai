"""Identity Anomaly Detection."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class IdentityAnomalyType(str, Enum):
    UNUSUAL_PRIVILEGE_USAGE = "UNUSUAL_PRIVILEGE_USAGE"
    UNUSUAL_ACCESS_TIMING = "UNUSUAL_ACCESS_TIMING"
    SUDDEN_ACCESS_EXPANSION = "SUDDEN_ACCESS_EXPANSION"
    ABNORMAL_AGENT_ACTIVITY = "ABNORMAL_AGENT_ACTIVITY"
    SERVICE_IDENTITY_MISUSE = "SERVICE_IDENTITY_MISUSE"


class IdentityAnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IdentityAnomalyStatus(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    CONFIRMED = "CONFIRMED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class IdentityAnomalyEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    data_points: Dict[str, Any] = Field(default_factory=dict)


class IdentityAnomaly(BaseModel):
    anomaly_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    anomaly_type: IdentityAnomalyType
    severity: IdentityAnomalySeverity = IdentityAnomalySeverity.MEDIUM
    status: IdentityAnomalyStatus = IdentityAnomalyStatus.DETECTED
    evidence: List[IdentityAnomalyEvidence] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityAnomalyManager:
    """Manages identity anomaly detection, tracking, and evidence collection."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, IdentityAnomaly] = {}

    def detect_anomaly(
        self,
        tenant_id: str,
        identity_id: str,
        anomaly_type: IdentityAnomalyType,
        severity: IdentityAnomalySeverity = IdentityAnomalySeverity.MEDIUM,
        description: str = "Behavioral deviation detected",
    ) -> IdentityAnomaly:
        evidence = [IdentityAnomalyEvidence(description=description)]
        anomaly = IdentityAnomaly(
            tenant_id=tenant_id,
            identity_id=identity_id,
            anomaly_type=anomaly_type,
            severity=severity,
            evidence=evidence,
        )
        self._anomalies[anomaly.anomaly_id] = anomaly
        return anomaly

    def get_anomaly(self, tenant_id: str, anomaly_id: str) -> IdentityAnomaly:
        anomaly = self._anomalies.get(anomaly_id)
        if not anomaly or anomaly.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return anomaly

    def list_anomalies(self, tenant_id: str, identity_id: Optional[str] = None) -> List[IdentityAnomaly]:
        res = []
        for a in self._anomalies.values():
            if a.tenant_id == tenant_id:
                if identity_id is None or a.identity_id == identity_id:
                    res.append(a)
        return res
