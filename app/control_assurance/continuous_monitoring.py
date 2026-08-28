"""Continuous Assurance Monitoring Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException


class MonitoringStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MonitoringSchedule(BaseModel):
    frequency_minutes: int = 60
    cron_expression: Optional[str] = "0 * * * *"
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None


class MonitoringPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"mpol_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    controls_in_scope: List[str] = Field(default_factory=list)
    schedule: MonitoringSchedule = Field(default_factory=MonitoringSchedule)
    is_enabled: bool = True


class ControlMonitoringSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"msess_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    policy_id: str
    status: MonitoringStatus = MonitoringStatus.ACTIVE
    evaluations_run_count: int = 0
    violations_detected_count: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContinuousMonitoringManager:
    """Manages continuous control monitoring policies and sessions."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._policies: Dict[str, MonitoringPolicy] = {}
        self._sessions: Dict[str, ControlMonitoringSession] = {}

    def create_monitoring_policy(
        self,
        tenant_id: str,
        name: str,
        controls_in_scope: List[str],
        frequency_minutes: int = 60,
    ) -> MonitoringPolicy:
        policy = MonitoringPolicy(
            tenant_id=tenant_id,
            name=name,
            controls_in_scope=controls_in_scope,
            schedule=MonitoringSchedule(frequency_minutes=frequency_minutes),
        )
        self._policies[policy.policy_id] = policy
        return policy

    def trigger_monitoring_session(self, policy_id: str, tenant_id: str) -> ControlMonitoringSession:
        pol = self._policies.get(policy_id)
        if not pol:
            raise CrossTenantControlAssuranceAccessException()
        try:
            self.tenant_guard.enforce_isolation(tenant_id, pol.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()

        sess = ControlMonitoringSession(
            tenant_id=tenant_id,
            policy_id=policy_id,
            status=MonitoringStatus.ACTIVE,
            evaluations_run_count=len(pol.controls_in_scope),
        )
        self._sessions[sess.session_id] = sess
        return sess
