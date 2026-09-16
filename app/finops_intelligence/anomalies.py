"""Financial Anomaly Detection (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class CostAnomalyType(str, Enum):
    SPENDING_SPIKE = "SPENDING_SPIKE"
    TOKEN_BURST = "TOKEN_BURST"
    UNUSUAL_MODEL_USAGE = "UNUSUAL_MODEL_USAGE"
    RUNAWAY_AGENT_COST = "RUNAWAY_AGENT_COST"
    DUPLICATE_BILLING = "DUPLICATE_BILLING"
    INFRASTRUCTURE_SPIKE = "INFRASTRUCTURE_SPIKE"


class CostAnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CostAnomalyStatus(str, Enum):
    DETECTED = "DETECTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    SUPPRESSED = "SUPPRESSED"


class CostAnomaly(BaseModel):
    anomaly_id: str = Field(default_factory=lambda: f"anom_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    anomaly_type: CostAnomalyType = CostAnomalyType.SPENDING_SPIKE
    severity: CostAnomalySeverity = CostAnomalySeverity.HIGH
    status: CostAnomalyStatus = CostAnomalyStatus.DETECTED
    expected_amount_usd: float = 0.0
    actual_amount_usd: float = 0.0
    deviation_pct: float = 0.0
    resource_id: str
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CostAnomalyManager:
    """Detects and manages financial anomalies and runaway cost spikes."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, CostAnomaly] = {}

    def detect_anomaly(
        self,
        tenant_id: str,
        resource_id: str,
        expected_amount_usd: float,
        actual_amount_usd: float,
        anomaly_type: CostAnomalyType = CostAnomalyType.SPENDING_SPIKE,
    ) -> Optional[CostAnomaly]:
        if expected_amount_usd <= 0:
            deviation = 100.0 if actual_amount_usd > 0 else 0.0
        else:
            deviation = round(((actual_amount_usd - expected_amount_usd) / expected_amount_usd) * 100.0, 2)

        if deviation < 50.0:
            return None  # Below anomaly threshold

        severity = CostAnomalySeverity.CRITICAL if deviation >= 200.0 else (CostAnomalySeverity.HIGH if deviation >= 100.0 else CostAnomalySeverity.MEDIUM)

        anom = CostAnomaly(
            tenant_id=tenant_id,
            resource_id=resource_id,
            anomaly_type=anomaly_type,
            severity=severity,
            expected_amount_usd=expected_amount_usd,
            actual_amount_usd=actual_amount_usd,
            deviation_pct=deviation,
        )
        self._anomalies[anom.anomaly_id] = anom
        return anom

    def get_anomaly(self, tenant_id: str, anomaly_id: str) -> CostAnomaly:
        anom = self._anomalies.get(anomaly_id)
        if not anom or anom.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return anom

    def list_anomalies(self, tenant_id: str) -> List[CostAnomaly]:
        return [a for a in self._anomalies.values() if a.tenant_id == tenant_id]
