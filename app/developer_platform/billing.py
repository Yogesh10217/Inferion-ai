"""Developer Platform Cost Attribution & Billing Aggregator."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DeveloperProjectBillingRecord(BaseModel):
    """Cost tracking container for developer projects."""

    project_id: str
    developer_id: str
    tenant_id: str = "global"
    organization_id: str
    workspace_id: str
    total_extension_executions: int = 0
    total_compute_seconds: float = 0.0
    total_memory_mb_seconds: float = 0.0
    total_api_calls: int = 0
    total_tokens: int = 0
    total_cost_dollars: float = 0.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeveloperBillingTracker:
    """Tracks developer project usage and cost attribution."""

    def __init__(self) -> None:
        self._records: Dict[str, DeveloperProjectBillingRecord] = {}

    def record_usage(
        self,
        project_id: str,
        developer_id: str,
        organization_id: str,
        workspace_id: str,
        tenant_id: str = "global",
        compute_seconds: float = 0.0,
        memory_mb_seconds: float = 0.0,
        api_calls: int = 1,
        tokens: int = 0,
        cost_dollars: float = 0.0,
    ) -> DeveloperProjectBillingRecord:
        """Record developer usage metrics into cost tracker."""
        if project_id not in self._records:
            self._records[project_id] = DeveloperProjectBillingRecord(
                project_id=project_id,
                developer_id=developer_id,
                tenant_id=tenant_id,
                organization_id=organization_id,
                workspace_id=workspace_id,
            )

        rec = self._records[project_id]
        rec.total_extension_executions += 1
        rec.total_compute_seconds += compute_seconds
        rec.total_memory_mb_seconds += memory_mb_seconds
        rec.total_api_calls += api_calls
        rec.total_tokens += tokens
        rec.total_cost_dollars += cost_dollars
        rec.updated_at = datetime.now(timezone.utc)
        return rec

    def get_billing_record(self, project_id: str) -> Optional[DeveloperProjectBillingRecord]:
        return self._records.get(project_id)
