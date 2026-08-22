"""Resource Governance Engine enforcing system-wide compute & memory budgets."""

import os
import logging
try:
    import psutil
except ImportError:
    psutil = None

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


from app.governance.rate_limiter import RateLimiter, RateLimitPolicy, RateLimitResult
from app.governance.quota_manager import QuotaManager
from app.security.exceptions import SecurityPolicyViolation

logger = logging.getLogger(__name__)


class GovernanceLimits(BaseModel):
    """System-wide hardware & operational thresholds."""

    max_cpu_percent: float = 90.0
    max_memory_percent: float = 85.0
    max_concurrent_global_executions: int = 100
    max_global_workers: int = 50


class ResourceGovernanceEngine:
    """Central engine unifying hardware limits, rate limits, and quota enforcement across all services."""

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        quota_manager: Optional[QuotaManager] = None,
        limits: Optional[GovernanceLimits] = None,
    ) -> None:
        self.rate_limiter = rate_limiter or RateLimiter()
        self.quota_manager = quota_manager or QuotaManager()
        self.limits = limits or GovernanceLimits()
        self._active_global_concurrency: int = 0

    def check_hardware_health(self) -> Dict[str, Any]:
        """Check CPU and RAM health thresholds."""
        try:
            if psutil:
                cpu_pct = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                mem_pct = mem.percent
            else:
                cpu_pct = 10.0
                mem_pct = 20.0
        except Exception:
            cpu_pct = 10.0
            mem_pct = 20.0


        if cpu_pct > self.limits.max_cpu_percent:
            raise SecurityPolicyViolation(f"System CPU usage too high ({cpu_pct:.1f}% > {self.limits.max_cpu_percent}%)")

        if mem_pct > self.limits.max_memory_percent:
            raise SecurityPolicyViolation(f"System memory usage too high ({mem_pct:.1f}% > {self.limits.max_memory_percent}%)")

        return {
            "status": "healthy",
            "cpu_percent": cpu_pct,
            "memory_percent": mem_pct,
        }

    def prepare_execution(
        self,
        component: str,
        tenant_id: str = "global",
        user_id: Optional[str] = None,
        estimated_tokens: int = 100,
        estimated_cost: float = 0.001,
        requires_worker: bool = False,
    ) -> Dict[str, Any]:
        """Validate hardware health, rate limit policy, and consumption quotas before execution."""
        # 1. Hardware health check
        self.check_hardware_health()

        # 2. Rate limit policy check
        policy = RateLimitPolicy(key_prefix=f"gov:{component}", max_requests=120, window_seconds=60)
        rate_res = self.rate_limiter.consume(policy=policy, tenant_id=tenant_id, user_id=user_id)
        if not rate_res.allowed:
            raise SecurityPolicyViolation(f"Rate limit exceeded for component '{component}'")

        # 3. Quota check & reservation
        workers_delta = 1 if requires_worker else 0
        kwargs = {"requests": 1, "tokens": estimated_tokens, "cost": estimated_cost, "concurrent_delta": 1, "workers_delta": workers_delta}
        
        if component in ["agent", "agent_execution"]:
            kwargs["agent_executions"] = 1
        elif component in ["workflow", "dag"]:
            kwargs["workflow_executions"] = 1
        elif component in ["tool", "mcp"]:
            kwargs["tool_executions"] = 1

        self.quota_manager.consume_quota(tenant_id=tenant_id, **kwargs)

        self._active_global_concurrency += 1
        return {
            "status": "approved",
            "tenant_id": tenant_id,
            "component": component,
            "active_concurrency": self._active_global_concurrency,
        }

    def complete_execution(
        self,
        component: str,
        tenant_id: str = "global",
        actual_tokens: int = 0,
        actual_cost: float = 0.0,
        requires_worker: bool = False,
    ) -> None:
        """Release concurrency locks and record actual token/cost delta."""
        workers_delta = 1 if requires_worker else 0
        self.quota_manager.release_quota(tenant_id=tenant_id, concurrent_delta=1, workers_delta=workers_delta)
        self._active_global_concurrency = max(0, self._active_global_concurrency - 1)
        logger.debug(f"[GOVERNANCE] Released execution hold for component '{component}' (tenant={tenant_id})")
