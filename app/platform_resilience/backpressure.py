"""Overload Protection Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException


class BackpressureLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BackpressureAction(str, Enum):
    QUEUE = "QUEUE"
    THROTTLE = "THROTTLE"
    DEFER = "DEFER"
    REJECT = "REJECT"
    DEGRADE = "DEGRADE"


class BackpressureSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"bpsig_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    level: BackpressureLevel = BackpressureLevel.NORMAL
    queue_depth: int = 0
    active_requests: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BackpressurePolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"bppoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    max_queue_depth: int = 1000
    warning_queue_depth: int = 500
    action: BackpressureAction = BackpressureAction.THROTTLE


class BackpressureAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"bpeval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    level: BackpressureLevel = BackpressureLevel.NORMAL
    recommended_action: BackpressureAction = BackpressureAction.QUEUE
    is_protection_active: bool = False


class BackpressureManager:
    """Overload protection assessment manager."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._policies: Dict[str, BackpressurePolicy] = {}

    def set_policy(
        self,
        tenant_id: str,
        service_id: str,
        max_queue_depth: int = 1000,
        action: BackpressureAction = BackpressureAction.THROTTLE,
    ) -> BackpressurePolicy:
        poly = BackpressurePolicy(
            tenant_id=tenant_id,
            service_id=service_id,
            max_queue_depth=max_queue_depth,
            action=action,
        )
        self._policies[f"{tenant_id}:{service_id}"] = poly
        return poly

    def evaluate_backpressure(
        self,
        tenant_id: str,
        service_id: str,
        current_queue_depth: int,
        active_requests: int = 0,
    ) -> BackpressureAssessment:
        policy = self._policies.get(f"{tenant_id}:{service_id}")
        max_depth = policy.max_queue_depth if policy else 1000
        warn_depth = policy.warning_queue_depth if policy else 500

        level = BackpressureLevel.NORMAL
        rec_action = BackpressureAction.QUEUE
        active = False

        if current_queue_depth >= max_depth:
            level = BackpressureLevel.CRITICAL
            rec_action = BackpressureAction.REJECT
            active = True
        elif current_queue_depth >= (max_depth * 0.85):
            level = BackpressureLevel.HIGH
            rec_action = BackpressureAction.DEFER
            active = True
        elif current_queue_depth >= warn_depth:
            level = BackpressureLevel.WARNING
            rec_action = BackpressureAction.THROTTLE
            active = True

        return BackpressureAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            level=level,
            recommended_action=rec_action,
            is_protection_active=active,
        )
