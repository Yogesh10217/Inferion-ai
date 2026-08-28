"""Distributed Rate Limit Policy Intelligence Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException


class RateLimitScope(str, Enum):
    TENANT = "TENANT"
    USER = "USER"
    SERVICE = "SERVICE"
    API = "API"
    AGENT = "AGENT"
    TOOL = "TOOL"
    GLOBAL = "GLOBAL"


class RateLimitWindow(str, Enum):
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"


class RateLimitPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"rlpoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    scope: RateLimitScope = RateLimitScope.TENANT
    target_id: str
    max_requests: int = 1000
    window: RateLimitWindow = RateLimitWindow.MINUTE


class RateLimitViolation(BaseModel):
    violation_id: str = Field(default_factory=lambda: f"rlviol_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    scope: RateLimitScope
    observed_requests: int
    allowed_requests: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RateLimitAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"rleval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    scope: RateLimitScope
    is_allowed: bool = True
    remaining_quota: int = 1000
    retry_after_seconds: int = 0


class RateLimitManager:
    """Distributed Rate Limit Policy Intelligence Manager."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._policies: Dict[str, RateLimitPolicy] = {}

    def set_rate_limit_policy(
        self,
        tenant_id: str,
        target_id: str,
        scope: RateLimitScope = RateLimitScope.TENANT,
        max_requests: int = 1000,
        window: RateLimitWindow = RateLimitWindow.MINUTE,
    ) -> RateLimitPolicy:
        poly = RateLimitPolicy(
            tenant_id=tenant_id,
            target_id=target_id,
            scope=scope,
            max_requests=max_requests,
            window=window,
        )
        self._policies[f"{tenant_id}:{scope.value}:{target_id}"] = poly
        return poly

    def evaluate_rate_limit(
        self,
        tenant_id: str,
        target_id: str,
        scope: RateLimitScope = RateLimitScope.TENANT,
        current_request_count: int = 1,
    ) -> RateLimitAssessment:
        policy = self._policies.get(f"{tenant_id}:{scope.value}:{target_id}")
        max_req = policy.max_requests if policy else 1000
        
        is_allowed = current_request_count <= max_req
        remaining = max(0, max_req - current_request_count)
        retry_after = 0 if is_allowed else 60

        return RateLimitAssessment(
            tenant_id=tenant_id,
            target_id=target_id,
            scope=scope,
            is_allowed=is_allowed,
            remaining_quota=remaining,
            retry_after_seconds=retry_after,
        )
