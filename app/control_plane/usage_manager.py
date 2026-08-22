"""Unified Usage Aggregator across all 16 platform subsystems."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AggregatedUsageRecord(BaseModel):
    """Unified usage metrics container."""

    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    resource_id: Optional[str] = None
    total_requests: int = 0
    total_agent_executions: int = 0
    total_workflow_executions: int = 0
    total_tool_executions: int = 0
    total_worker_jobs: int = 0
    total_tokens: int = 0
    total_cost_dollars: float = 0.0
    storage_bytes_used: int = 0
    total_failures: int = 0
    total_retries: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlPlaneUsageManager:
    """Aggregates usage telemetry across Gateway, Models, Agents, Workflows, Tools, Workers, Storage."""

    def __init__(self) -> None:
        self._usage_records: Dict[str, AggregatedUsageRecord] = {}

    def _get_or_create(self, tenant_id: str, organization_id: Optional[str] = None, workspace_id: Optional[str] = None) -> AggregatedUsageRecord:
        key = f"{tenant_id}:{organization_id or 'none'}:{workspace_id or 'none'}"
        if key not in self._usage_records:
            self._usage_records[key] = AggregatedUsageRecord(
                tenant_id=tenant_id,
                organization_id=organization_id,
                workspace_id=workspace_id,
            )
        return self._usage_records[key]

    def record_event(
        self,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        requests: int = 0,
        agent_executions: int = 0,
        workflow_executions: int = 0,
        tool_executions: int = 0,
        worker_jobs: int = 0,
        tokens: int = 0,
        cost_dollars: float = 0.0,
        storage_bytes: int = 0,
        failures: int = 0,
        retries: int = 0,
    ) -> AggregatedUsageRecord:
        """Record usage event metrics into aggregated telemetry store."""
        rec = self._get_or_create(tenant_id, organization_id, workspace_id)
        rec.total_requests += requests
        rec.total_agent_executions += agent_executions
        rec.total_workflow_executions += workflow_executions
        rec.total_tool_executions += tool_executions
        rec.total_worker_jobs += worker_jobs
        rec.total_tokens += tokens
        rec.total_cost_dollars += cost_dollars
        rec.storage_bytes_used += storage_bytes
        rec.total_failures += failures
        rec.total_retries += retries
        rec.timestamp = datetime.now(timezone.utc)
        return rec

    def get_usage(self, tenant_id: str = "global", organization_id: Optional[str] = None, workspace_id: Optional[str] = None) -> AggregatedUsageRecord:
        return self._get_or_create(tenant_id, organization_id, workspace_id)
