"""Drift & Performance Regression Detection Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.mlops.deployment import DeploymentManager, DeploymentStatus

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DriftType(str, Enum):
    INPUT_DRIFT = "INPUT_DRIFT"
    OUTPUT_DRIFT = "OUTPUT_DRIFT"
    PERFORMANCE_DRIFT = "PERFORMANCE_DRIFT"
    LATENCY_DRIFT = "LATENCY_DRIFT"
    COST_DRIFT = "COST_DRIFT"
    QUALITY_REGRESSION = "QUALITY_REGRESSION"
    SAFETY_REGRESSION = "SAFETY_REGRESSION"


class DriftResult(BaseModel):
    event_id: str = Field(default_factory=lambda: f"drift_{uuid.uuid4().hex[:10]}")
    deployment_id: str
    tenant_id: str = "global"
    drift_type: DriftType
    severity: str = "HIGH"  # LOW, MEDIUM, HIGH, CRITICAL
    baseline_value: float
    current_value: float
    deviation_percent: float
    action_taken: str = "ALERT_AND_DEGRADE"
    detected_at: datetime = Field(default_factory=_now)


class DriftDetector:
    """Monitors live deployments for feature input drift, output distribution drift, and performance regressions."""

    def __init__(self, deployment_manager: Optional[DeploymentManager] = None) -> None:
        self.deployment_manager = deployment_manager or DeploymentManager()
        self._events: List[DriftResult] = []

    def detect_drift(
        self,
        deployment_id: str,
        drift_type: DriftType,
        baseline_value: float,
        current_value: float,
        threshold_percent: float = 20.0,
        tenant_id: str = "global",
    ) -> Optional[DriftResult]:
        diff = abs(current_value - baseline_value)
        dev_percent = (diff / baseline_value * 100.0) if baseline_value != 0 else 0.0

        if dev_percent >= threshold_percent:
            severity = "CRITICAL" if dev_percent >= 50.0 else "HIGH"
            res = DriftResult(
                deployment_id=deployment_id,
                tenant_id=tenant_id,
                drift_type=drift_type,
                severity=severity,
                baseline_value=baseline_value,
                current_value=current_value,
                deviation_percent=dev_percent,
            )
            self._events.append(res)

            # Mark deployment DEGRADED if critical drift
            try:
                dep = self.deployment_manager.get_deployment(deployment_id)
                dep.status = DeploymentStatus.DEGRADED
            except Exception:
                pass

            logger.warning(f"[DRIFT DETECTOR] Detected '{drift_type.value}' ({dev_percent:.1f}% deviation) on deployment '{deployment_id}' -> Marked DEGRADED")
            return res

        return None

    def compute_psi_divergence(self, baseline_dist: List[float], current_dist: List[float]) -> float:
        """Compute Population Stability Index (PSI) divergence between baseline and current distributions."""
        if len(baseline_dist) != len(current_dist) or not baseline_dist:
            return 0.0

        psi = 0.0
        eps = 1e-4
        b_sum = sum(baseline_dist) or 1.0
        c_sum = sum(current_dist) or 1.0

        for b, c in zip(baseline_dist, current_dist):
            b_pct = (b / b_sum) + eps
            c_pct = (c / c_sum) + eps
            import math
            psi += (c_pct - b_pct) * math.log(c_pct / b_pct)

        return round(psi, 4)

    def list_drift_events(self, deployment_id: Optional[str] = None, tenant_id: Optional[str] = None) -> List[DriftResult]:
        res = self._events
        if deployment_id:
            res = [e for e in res if e.deployment_id == deployment_id]
        if tenant_id:
            res = [e for e in res if e.tenant_id == tenant_id]
        return res
