"""Drift & Degradation Intelligence Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import CrossTenantLifecycleAccessException


class DriftType(str, Enum):
    DATA_DRIFT = "DATA_DRIFT"
    PERFORMANCE_DRIFT = "PERFORMANCE_DRIFT"
    BEHAVIOR_DRIFT = "BEHAVIOR_DRIFT"
    COST_DRIFT = "COST_DRIFT"
    SAFETY_DRIFT = "SAFETY_DRIFT"
    SECURITY_DRIFT = "SECURITY_DRIFT"
    CONFIGURATION_DRIFT = "CONFIGURATION_DRIFT"


class DriftSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DriftStatus(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATED = "MITIGATED"
    IGNORED = "IGNORED"


class DriftEvidence(BaseModel):
    metric_name: str
    baseline_value: float
    current_value: float
    p_value: float = 0.01


class DriftDetection(BaseModel):
    drift_id: str = Field(default_factory=lambda: f"drift_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    drift_type: DriftType = DriftType.PERFORMANCE_DRIFT
    severity: DriftSeverity = DriftSeverity.MEDIUM
    status: DriftStatus = DriftStatus.DETECTED
    evidence: Optional[DriftEvidence] = None
    recommendations: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DriftManager:
    """Detects drift and degradation producing evidence and non-mutating recommendations."""

    def __init__(self) -> None:
        self._drifts: Dict[str, DriftDetection] = {}

    def detect_drift(
        self,
        tenant_id: str,
        asset_id: str,
        drift_type: DriftType = DriftType.PERFORMANCE_DRIFT,
        severity: DriftSeverity = DriftSeverity.HIGH,
        baseline_val: float = 0.95,
        current_val: float = 0.70,
    ) -> DriftDetection:
        ev = DriftEvidence(metric_name=drift_type.value, baseline_value=baseline_val, current_value=current_val)
        recs = []
        if severity in (DriftSeverity.HIGH, DriftSeverity.CRITICAL):
            recs = ["RE_EVALUATION_REQUIRED", "PROMOTION_BLOCK", "ROLLBACK_RECOMMENDED"]

        drift = DriftDetection(
            tenant_id=tenant_id,
            asset_id=asset_id,
            drift_type=drift_type,
            severity=severity,
            evidence=ev,
            recommendations=recs,
        )
        self._drifts[drift.drift_id] = drift
        return drift

    def get_drift(self, drift_id: str, tenant_id: str) -> DriftDetection:
        drift = self._drifts.get(drift_id)
        if not drift:
            raise KeyError(f"Drift '{drift_id}' not found.")
        if tenant_id != "global" and drift.tenant_id != "global" and tenant_id != drift.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, drift.tenant_id)
        return drift

    def list_drifts(self, tenant_id: str) -> List[DriftDetection]:
        return [d for d in self._drifts.values() if d.tenant_id == tenant_id]
