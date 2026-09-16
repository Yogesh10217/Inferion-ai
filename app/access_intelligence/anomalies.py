"""Access Anomaly Intelligence (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class AccessAnomalyType(str, Enum):
    UNUSUAL_PRIVILEGE_USAGE = "UNUSUAL_PRIVILEGE_USAGE"
    ABNORMAL_ACCESS_TIMING = "ABNORMAL_ACCESS_TIMING"
    UNUSUAL_RESOURCE_ACCESS = "UNUSUAL_RESOURCE_ACCESS"
    DORMANT_IDENTITY_ACTIVATION = "DORMANT_IDENTITY_ACTIVATION"
    PRIVILEGE_ESCALATION_SEQUENCE = "PRIVILEGE_ESCALATION_SEQUENCE"
    AGENT_TOOL_MISUSE = "AGENT_TOOL_MISUSE"


class AccessAnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccessAnomalyConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AccessAnomalyEvidence(BaseModel):
    """Telemetry evidence supporting access anomaly finding."""
    evidence_id: str = Field(default_factory=lambda: f"anom_evid_{uuid.uuid4().hex[:8]}")
    source_signal_id: Optional[str] = None
    baseline_value: str = ""
    observed_value: str = ""
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class AccessAnomaly(BaseModel):
    """Access Anomaly Finding Representation."""
    anomaly_id: str = Field(default_factory=lambda: f"anom_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    subject_identity_id: str
    anomaly_type: AccessAnomalyType
    severity: AccessAnomalySeverity = AccessAnomalySeverity.HIGH
    confidence: AccessAnomalyConfidence = AccessAnomalyConfidence.HIGH
    title: str
    description: str
    evidence: AccessAnomalyEvidence
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_resolved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessAnomalyManager:
    """Manages access anomaly detection and findings."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, AccessAnomaly] = {}

    def detect_anomaly(
        self,
        tenant_id: str,
        subject_identity_id: str,
        anomaly_type: AccessAnomalyType,
        title: str,
        description: str,
        baseline_value: str = "",
        observed_value: str = "",
        severity: AccessAnomalySeverity = AccessAnomalySeverity.HIGH,
        confidence: AccessAnomalyConfidence = AccessAnomalyConfidence.HIGH,
        source_signal_id: Optional[str] = None,
        raw_payload: Optional[Dict[str, Any]] = None,
    ) -> AccessAnomaly:
        evid = AccessAnomalyEvidence(
            source_signal_id=source_signal_id,
            baseline_value=baseline_value,
            observed_value=observed_value,
            raw_payload=raw_payload or {},
        )
        anom = AccessAnomaly(
            tenant_id=tenant_id,
            subject_identity_id=subject_identity_id,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            title=title,
            description=description,
            evidence=evid,
        )
        self._anomalies[anom.anomaly_id] = anom
        return anom

    def get_anomaly(self, tenant_id: str, anomaly_id: str) -> AccessAnomaly:
        anom = self._anomalies.get(anomaly_id)
        if not anom or anom.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return anom

    def list_anomalies(
        self,
        tenant_id: str,
        anomaly_type: Optional[AccessAnomalyType] = None,
        severity: Optional[AccessAnomalySeverity] = None,
    ) -> List[AccessAnomaly]:
        results = [a for a in self._anomalies.values() if a.tenant_id == tenant_id]
        if anomaly_type:
            results = [a for a in results if a.anomaly_type == anomaly_type]
        if severity:
            results = [a for a in results if a.severity == severity]
        return results
