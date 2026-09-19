"""Model Anomaly Detection (Phase 5.44)."""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelAnomalyType(str, Enum):
    LATENCY_SPIKE = "LATENCY_SPIKE"
    OUTPUT_ANOMALY = "OUTPUT_ANOMALY"
    FAILURE_SPIKE = "FAILURE_SPIKE"
    BEHAVIOR_CHANGE = "BEHAVIOR_CHANGE"
    COST_SPIKE = "COST_SPIKE"
    QUALITY_DEGRADATION = "QUALITY_DEGRADATION"


class ModelAnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ModelAnomalyStatus(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ModelAnomalyEvidence(BaseModel):
    evidence_id: str
    metric_name: str
    observed_value: float
    expected_threshold: float
    fingerprint: str


class ModelAnomaly(BaseModel):
    anomaly_id: str
    model_id: str
    tenant_id: str
    anomaly_type: ModelAnomalyType
    severity: ModelAnomalySeverity
    status: ModelAnomalyStatus = ModelAnomalyStatus.DETECTED
    evidence: ModelAnomalyEvidence
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelAnomalyManager:
    """Manages model anomaly detection and lifecycle."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, ModelAnomaly] = {}

    def detect_anomaly(
        self,
        model_id: str,
        tenant_id: str,
        anomaly_type: ModelAnomalyType,
        metric_name: str,
        observed_value: float,
        expected_threshold: float,
        severity: ModelAnomalySeverity = ModelAnomalySeverity.HIGH,
    ) -> ModelAnomaly:
        a_id = f"anom-{uuid.uuid4().hex[:8]}"

        fp = hashlib.sha256(f"{model_id}:{anomaly_type}:{observed_value}:{expected_threshold}".encode()).hexdigest()

        evidence = ModelAnomalyEvidence(
            evidence_id=f"aevid-{uuid.uuid4().hex[:6]}",
            metric_name=metric_name,
            observed_value=observed_value,
            expected_threshold=expected_threshold,
            fingerprint=fp,
        )

        anomaly = ModelAnomaly(
            anomaly_id=a_id,
            model_id=model_id,
            tenant_id=tenant_id,
            anomaly_type=anomaly_type,
            severity=severity,
            evidence=evidence,
        )

        self._anomalies[a_id] = anomaly
        logger.info(
            f"[MODEL ANOMALY] Detected {anomaly_type} for model {model_id} (Tenant: {tenant_id}) Severity: {severity}"
        )
        return anomaly

    def list_anomalies(self, tenant_id: str, model_id: Optional[str] = None) -> List[ModelAnomaly]:
        res = [a for a in self._anomalies.values() if a.tenant_id == tenant_id]
        if model_id:
            res = [a for a in res if a.model_id == model_id]
        return res
