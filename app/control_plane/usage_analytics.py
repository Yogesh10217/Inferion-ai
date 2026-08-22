"""Usage Analytics Generator for Tenant, Org, Workspace, and Cost Reports."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.control_plane.usage_manager import ControlPlaneUsageManager

logger = logging.getLogger(__name__)


class ControlPlaneUsageAnalytics:
    """Generates analytics reports and cost breakdowns across scopes."""

    def __init__(self, usage_manager: Optional[ControlPlaneUsageManager] = None) -> None:
        self.usage_manager = usage_manager or ControlPlaneUsageManager()

    def generate_tenant_report(self, tenant_id: str) -> Dict[str, Any]:
        """Generate comprehensive usage and cost analytics report for a tenant."""
        rec = self.usage_manager.get_usage(tenant_id=tenant_id)

        return {
            "tenant_id": tenant_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_requests": rec.total_requests,
                "total_agent_executions": rec.total_agent_executions,
                "total_workflow_executions": rec.total_workflow_executions,
                "total_tool_executions": rec.total_tool_executions,
                "total_worker_jobs": rec.total_worker_jobs,
                "total_tokens": rec.total_tokens,
                "total_cost_dollars": round(rec.total_cost_dollars, 4),
                "storage_bytes": rec.storage_bytes_used,
                "failure_rate": round(rec.total_failures / max(1, rec.total_requests), 4),
            },
        }

    def generate_cost_breakdown(self, tenant_id: str) -> Dict[str, Any]:
        """Generate detailed cost distribution report."""
        rec = self.usage_manager.get_usage(tenant_id=tenant_id)
        total_cost = rec.total_cost_dollars

        # Estimate component cost breakdown
        model_cost = total_cost * 0.7
        compute_cost = total_cost * 0.2
        storage_cost = total_cost * 0.1

        return {
            "tenant_id": tenant_id,
            "total_cost_dollars": round(total_cost, 4),
            "breakdown": {
                "models_cost_dollars": round(model_cost, 4),
                "compute_cost_dollars": round(compute_cost, 4),
                "storage_cost_dollars": round(storage_cost, 4),
            },
        }
