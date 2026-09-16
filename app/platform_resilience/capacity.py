"""Enterprise Capacity Intelligence Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard


class CapacityStatus(str, Enum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    SATURATED = "SATURATED"
    EXHAUSTED = "EXHAUSTED"


class CapacityMetric(BaseModel):
    metric_name: str
    current_value: float
    max_capacity: float
    unit: str = "percentage"
    utilization_pct: float = 0.0


class CapacityThreshold(BaseModel):
    warning_threshold_pct: float = 70.0
    high_threshold_pct: float = 85.0
    critical_threshold_pct: float = 95.0


class CapacityForecast(BaseModel):
    service_id: str
    timeframe_hours: int = 24
    projected_utilization_pct: float = 50.0
    is_scale_up_recommended: bool = False


class CapacityProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"capprof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    metrics: Dict[str, CapacityMetric] = Field(default_factory=dict)
    thresholds: CapacityThreshold = Field(default_factory=CapacityThreshold)
    status: CapacityStatus = CapacityStatus.NORMAL
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CapacityAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"capeval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    status: CapacityStatus = CapacityStatus.NORMAL
    max_utilization_pct: float = 0.0
    recommendation: str = "NO_ACTION"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CapacityManager:
    """Enterprise Capacity Intelligence Manager for capacity monitoring and forecasting."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._profiles: Dict[str, CapacityProfile] = {}

    def register_capacity_profile(
        self,
        tenant_id: str,
        resource_id: str,
        metrics: Optional[Dict[str, CapacityMetric]] = None,
        thresholds: Optional[CapacityThreshold] = None,
    ) -> CapacityProfile:
        prof = CapacityProfile(
            tenant_id=tenant_id,
            resource_id=resource_id,
            metrics=metrics or {},
            thresholds=thresholds or CapacityThreshold(),
        )
        self._profiles[prof.profile_id] = prof
        return prof

    def evaluate_capacity(self, tenant_id: str, resource_id: str) -> CapacityAssessment:
        profile = next((p for p in self._profiles.values() if p.resource_id == resource_id and p.tenant_id == tenant_id), None)
        if not profile:
            # Default normal assessment
            return CapacityAssessment(tenant_id=tenant_id, resource_id=resource_id, status=CapacityStatus.NORMAL)

        max_util = max([m.utilization_pct for m in profile.metrics.values()], default=0.0)

        status = CapacityStatus.NORMAL
        recommendation = "NO_ACTION"

        if max_util >= profile.thresholds.critical_threshold_pct:
            status = CapacityStatus.EXHAUSTED if max_util >= 98.0 else CapacityStatus.SATURATED
            recommendation = "SCALE_OUT_IMMEDIATE"
        elif max_util >= profile.thresholds.high_threshold_pct:
            status = CapacityStatus.HIGH
            recommendation = "SCALE_OUT_RECOMMENDED"
        elif max_util >= profile.thresholds.warning_threshold_pct:
            status = CapacityStatus.ELEVATED
            recommendation = "MONITOR_CLOSELY"

        return CapacityAssessment(
            tenant_id=tenant_id,
            resource_id=resource_id,
            status=status,
            max_utilization_pct=max_util,
            recommendation=recommendation,
        )

    def forecast_capacity(self, tenant_id: str, resource_id: str, hours: int = 24) -> CapacityForecast:
        eval_res = self.evaluate_capacity(tenant_id, resource_id)
        proj_util = min(100.0, eval_res.max_utilization_pct + (hours * 0.5))
        return CapacityForecast(
            service_id=resource_id,
            timeframe_hours=hours,
            projected_utilization_pct=proj_util,
            is_scale_up_recommended=(proj_util > 85.0),
        )
