"""Continuous Model Monitoring (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class MonitoringStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    PAUSED = "PAUSED"


class MonitoringSignal(BaseModel):
    signal_id: str
    signal_type: str  # performance, drift, quality, reliability, safety, security
    severity: str = "INFO"
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelMonitoringProfile(BaseModel):
    profile_id: str
    model_id: str
    tenant_id: str
    enabled: bool = True
    sampling_rate: float = 1.0
    status: MonitoringStatus = MonitoringStatus.HEALTHY
    signals: List[MonitoringSignal] = Field(default_factory=list)


class MonitoringAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    status: MonitoringStatus
    active_warnings: int
    active_criticals: int
    recommendation: str = "CONTINUE_MONITORING"
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelMonitoringManager:
    """Manages continuous model monitoring across performance, drift, quality, reliability, safety, and security."""

    def __init__(self) -> None:
        self._profiles: Dict[str, ModelMonitoringProfile] = {}

    def configure_monitoring(
        self,
        model_id: str,
        tenant_id: str,
        sampling_rate: float = 1.0,
    ) -> ModelMonitoringProfile:
        prof_id = f"monprof-{uuid.uuid4().hex[:8]}"
        profile = ModelMonitoringProfile(
            profile_id=prof_id,
            model_id=model_id,
            tenant_id=tenant_id,
            sampling_rate=sampling_rate,
        )
        self._profiles[model_id] = profile
        logger.info(
            f"[MODEL MONITORING] Configured profile for model {model_id} (Tenant: {tenant_id}) Rate: {sampling_rate}"
        )
        return profile

    def record_signal(
        self,
        model_id: str,
        tenant_id: str,
        signal_type: str,
        severity: str,
        message: str,
    ) -> MonitoringSignal:
        prof = self._profiles.get(model_id)
        if not prof:
            prof = self.configure_monitoring(model_id, tenant_id)
        if prof.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()

        sig = MonitoringSignal(
            signal_id=f"sig-{uuid.uuid4().hex[:6]}",
            signal_type=signal_type,
            severity=severity,
            message=message,
        )
        prof.signals.append(sig)

        if severity == "CRITICAL":
            prof.status = MonitoringStatus.CRITICAL
        elif severity == "WARNING" and prof.status != MonitoringStatus.CRITICAL:
            prof.status = MonitoringStatus.WARNING

        return sig

    def assess_monitoring(self, model_id: str, tenant_id: str) -> MonitoringAssessment:
        prof = self._profiles.get(model_id)
        if not prof:
            return MonitoringAssessment(
                assessment_id=f"massess-{uuid.uuid4().hex[:8]}",
                model_id=model_id,
                tenant_id=tenant_id,
                status=MonitoringStatus.HEALTHY,
                active_warnings=0,
                active_criticals=0,
            )
        if prof.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()

        warns = sum(1 for s in prof.signals if s.severity == "WARNING")
        crits = sum(1 for s in prof.signals if s.severity == "CRITICAL")

        rec = "TRIGGER_REMEDIATION" if crits > 0 else ("INVESTIGATE_WARNINGS" if warns > 0 else "CONTINUE_MONITORING")

        return MonitoringAssessment(
            assessment_id=f"massess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            status=prof.status,
            active_warnings=warns,
            active_criticals=crits,
            recommendation=rec,
        )
