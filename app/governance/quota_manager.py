"""Quota Manager for Resource Allocations & Multi-Tenant Consumption."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field

from app.security.exceptions import QuotaExceededError

logger = logging.getLogger(__name__)


class QuotaDefinition(BaseModel):
    """Quota limit definitions for a tenant, organization, or user."""

    tenant_id: str = "global"
    max_requests_per_day: int = 10000
    max_tokens_per_day: int = 1000000
    max_cost_dollars_per_month: float = 100.0
    max_storage_bytes: int = 10 * 1024 * 1024 * 1024  # 10 GB
    max_agent_executions_per_day: int = 500
    max_workflow_executions_per_day: int = 200
    max_tool_executions_per_day: int = 2000
    max_concurrent_executions: int = 20
    max_digital_workers: int = 5


class QuotaUsage(BaseModel):
    """Current recorded quota usage metrics."""

    tenant_id: str
    requests_today: int = 0
    tokens_today: int = 0
    cost_this_month: float = 0.0
    storage_bytes_used: int = 0
    agent_executions_today: int = 0
    workflow_executions_today: int = 0
    tool_executions_today: int = 0
    current_concurrent_executions: int = 0
    active_digital_workers: int = 0
    last_reset_day: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    last_reset_month: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m"))


class QuotaManager:
    """Manages multi-resource usage tracking and quota limit enforcement."""

    def __init__(self) -> None:
        self._definitions: Dict[str, QuotaDefinition] = {}
        self._usage: Dict[str, QuotaUsage] = {}

    def set_definition(self, definition: QuotaDefinition) -> None:
        """Set or update quota definition for a tenant."""
        self._definitions[definition.tenant_id] = definition
        logger.info(f"[QUOTA] Set definition for tenant '{definition.tenant_id}'")

    def get_definition(self, tenant_id: str) -> QuotaDefinition:
        """Get quota definition for tenant, falling back to default."""
        return self._definitions.get(tenant_id, QuotaDefinition(tenant_id=tenant_id))

    def get_usage(self, tenant_id: str) -> QuotaUsage:
        """Get current usage for tenant with automatic daily/monthly resets."""
        now = datetime.now(timezone.utc)
        current_day = now.strftime("%Y-%m-%d")
        current_month = now.strftime("%Y-%m")

        if tenant_id not in self._usage:
            self._usage[tenant_id] = QuotaUsage(
                tenant_id=tenant_id,
                last_reset_day=current_day,
                last_reset_month=current_month,
            )

        u = self._usage[tenant_id]

        # Reset daily counters if new day
        if u.last_reset_day != current_day:
            u.requests_today = 0
            u.tokens_today = 0
            u.agent_executions_today = 0
            u.workflow_executions_today = 0
            u.tool_executions_today = 0
            u.last_reset_day = current_day

        # Reset monthly counters if new month
        if u.last_reset_month != current_month:
            u.cost_this_month = 0.0
            u.last_reset_month = current_month

        return u

    def check_quota(
        self,
        tenant_id: str,
        requests: int = 0,
        tokens: int = 0,
        cost: float = 0.0,
        storage_bytes: int = 0,
        agent_executions: int = 0,
        workflow_executions: int = 0,
        tool_executions: int = 0,
        concurrent_delta: int = 0,
        workers_delta: int = 0,
    ) -> bool:
        """Check if tenant has sufficient remaining quota for the requested operation."""
        defn = self.get_definition(tenant_id)
        u = self.get_usage(tenant_id)

        if requests > 0 and (u.requests_today + requests) > defn.max_requests_per_day:
            raise QuotaExceededError(f"Daily request quota exceeded ({defn.max_requests_per_day})")

        if tokens > 0 and (u.tokens_today + tokens) > defn.max_tokens_per_day:
            raise QuotaExceededError(f"Daily token quota exceeded ({defn.max_tokens_per_day})")

        if cost > 0.0 and (u.cost_this_month + cost) > defn.max_cost_dollars_per_month:
            raise QuotaExceededError(f"Monthly cost quota exceeded (${defn.max_cost_dollars_per_month:.2f})")

        if storage_bytes > 0 and (u.storage_bytes_used + storage_bytes) > defn.max_storage_bytes:
            raise QuotaExceededError(f"Storage quota exceeded ({defn.max_storage_bytes} bytes)")

        if agent_executions > 0 and (u.agent_executions_today + agent_executions) > defn.max_agent_executions_per_day:
            raise QuotaExceededError(f"Daily agent execution quota exceeded ({defn.max_agent_executions_per_day})")

        if workflow_executions > 0 and (u.workflow_executions_today + workflow_executions) > defn.max_workflow_executions_per_day:
            raise QuotaExceededError(f"Daily workflow execution quota exceeded ({defn.max_workflow_executions_per_day})")

        if tool_executions > 0 and (u.tool_executions_today + tool_executions) > defn.max_tool_executions_per_day:
            raise QuotaExceededError(f"Daily tool execution quota exceeded ({defn.max_tool_executions_per_day})")

        if concurrent_delta > 0 and (u.current_concurrent_executions + concurrent_delta) > defn.max_concurrent_executions:
            raise QuotaExceededError(f"Max concurrent execution quota exceeded ({defn.max_concurrent_executions})")

        if workers_delta > 0 and (u.active_digital_workers + workers_delta) > defn.max_digital_workers:
            raise QuotaExceededError(f"Digital worker quota exceeded ({defn.max_digital_workers})")

        return True

    def consume_quota(
        self,
        tenant_id: str,
        requests: int = 0,
        tokens: int = 0,
        cost: float = 0.0,
        storage_bytes: int = 0,
        agent_executions: int = 0,
        workflow_executions: int = 0,
        tool_executions: int = 0,
        concurrent_delta: int = 0,
        workers_delta: int = 0,
    ) -> QuotaUsage:
        """Consume quota units for a tenant after checking limits."""
        self.check_quota(
            tenant_id=tenant_id,
            requests=requests,
            tokens=tokens,
            cost=cost,
            storage_bytes=storage_bytes,
            agent_executions=agent_executions,
            workflow_executions=workflow_executions,
            tool_executions=tool_executions,
            concurrent_delta=concurrent_delta,
            workers_delta=workers_delta,
        )
        u = self.get_usage(tenant_id)
        u.requests_today += requests
        u.tokens_today += tokens
        u.cost_this_month += cost
        u.storage_bytes_used += storage_bytes
        u.agent_executions_today += agent_executions
        u.workflow_executions_today += workflow_executions
        u.tool_executions_today += tool_executions
        u.current_concurrent_executions = max(0, u.current_concurrent_executions + concurrent_delta)
        u.active_digital_workers = max(0, u.active_digital_workers + workers_delta)
        return u

    def release_quota(
        self,
        tenant_id: str,
        concurrent_delta: int = 0,
        workers_delta: int = 0,
        storage_bytes: int = 0,
    ) -> QuotaUsage:
        """Release temporary quota holds (concurrency, workers, deleted storage)."""
        u = self.get_usage(tenant_id)
        if concurrent_delta > 0:
            u.current_concurrent_executions = max(0, u.current_concurrent_executions - concurrent_delta)
        if workers_delta > 0:
            u.active_digital_workers = max(0, u.active_digital_workers - workers_delta)
        if storage_bytes > 0:
            u.storage_bytes_used = max(0, u.storage_bytes_used - storage_bytes)
        return u

    def get_remaining(self, tenant_id: str) -> Dict[str, Any]:
        """Get remaining quota capacity dictionary for tenant."""
        defn = self.get_definition(tenant_id)
        u = self.get_usage(tenant_id)

        return {
            "tenant_id": tenant_id,
            "remaining_requests_today": max(0, defn.max_requests_per_day - u.requests_today),
            "remaining_tokens_today": max(0, defn.max_tokens_per_day - u.tokens_today),
            "remaining_cost_month": max(0.0, defn.max_cost_dollars_per_month - u.cost_this_month),
            "remaining_storage_bytes": max(0, defn.max_storage_bytes - u.storage_bytes_used),
            "remaining_agent_executions_today": max(0, defn.max_agent_executions_per_day - u.agent_executions_today),
            "remaining_workflow_executions_today": max(0, defn.max_workflow_executions_per_day - u.workflow_executions_today),
            "remaining_tool_executions_today": max(0, defn.max_tool_executions_per_day - u.tool_executions_today),
            "remaining_concurrent_slots": max(0, defn.max_concurrent_executions - u.current_concurrent_executions),
            "remaining_worker_slots": max(0, defn.max_digital_workers - u.active_digital_workers),
        }
