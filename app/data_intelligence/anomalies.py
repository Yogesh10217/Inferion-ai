"""Data anomaly detection intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException, DataAnomalyNotFoundException


class DataAnomalyType(str, Enum):
    UNUSUAL_VOLUME = "UNUSUAL_VOLUME"
    MISSING_RECORDS = "MISSING_RECORDS"
    DUPLICATE_SPIKE = "DUPLICATE_SPIKE"
    ABNORMAL_NULL_RATE = "ABNORMAL_NULL_RATE"
    UNEXPECTED_VALUE_DISTRIBUTION = "UNEXPECTED_VALUE_DISTRIBUTION"
    UNEXPECTED_SCHEMA_CHANGE = "UNEXPECTED_SCHEMA_CHANGE"
    ABNORMAL_PIPELINE_OUTPUT = "ABNORMAL_PIPELINE_OUTPUT"


class DataAnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DataAnomalyStatus(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"


class DataAnomalyEvidence(BaseModel):
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_pct: float
    description: str


class DataAnomaly(BaseModel):
    anomaly_id: str
    dataset_id: str
    tenant_id: str
    anomaly_type: DataAnomalyType
    severity: DataAnomalySeverity
    status: DataAnomalyStatus = DataAnomalyStatus.DETECTED
    evidence: DataAnomalyEvidence
    description: str
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataAnomalyManager:
    """Manages detection and lifecycle of data anomalies."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, DataAnomaly] = {}

    def detect_anomaly(
        self,
        dataset_id: str,
        tenant_id: str,
        anomaly_type: DataAnomalyType,
        severity: DataAnomalySeverity,
        metric_name: str,
        expected_value: float,
        actual_value: float,
        description: str = "",
        anomaly_id: Optional[str] = None,
    ) -> DataAnomaly:
        aid = anomaly_id or f"anom-{uuid.uuid4().hex[:8]}"
        dev_pct = abs(actual_value - expected_value) / max(0.0001, abs(expected_value)) * 100.0

        ev = DataAnomalyEvidence(
            metric_name=metric_name,
            expected_value=expected_value,
            actual_value=actual_value,
            deviation_pct=round(dev_pct, 2),
            description=description or f"Metric {metric_name} deviated by {dev_pct:.1f}% from expected {expected_value}",
        )

        anom = DataAnomaly(
            anomaly_id=aid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            anomaly_type=anomaly_type,
            severity=severity,
            evidence=ev,
            description=description or ev.description,
        )
        self._anomalies[aid] = anom
        return anom

    def get_anomaly(self, anomaly_id: str, tenant_id: str) -> DataAnomaly:
        anom = self._anomalies.get(anomaly_id)
        if not anom:
            raise DataAnomalyNotFoundException(anomaly_id)
        if anom.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return anom

    def list_anomalies(self, tenant_id: str, dataset_id: Optional[str] = None) -> List[DataAnomaly]:
        res = [a for a in self._anomalies.values() if a.tenant_id == tenant_id]
        if dataset_id:
            res = [a for a in res if a.dataset_id == dataset_id]
        return res

    def update_status(self, anomaly_id: str, tenant_id: str, status: DataAnomalyStatus) -> DataAnomaly:
        anom = self.get_anomaly(anomaly_id, tenant_id)
        anom.status = status
        return anom
