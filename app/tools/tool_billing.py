"""
Tool Billing and Usage Accounting Tracker
"""

import threading
import logging
from typing import Dict, Any

from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult

logger = logging.getLogger(__name__)


class ToolBillingTracker:
    """Tracks execution counts, duration, compute, storage, and cost attribution per tenant."""

    def __init__(self):
        self._lock = threading.RLock()
        self._tenant_usage: Dict[str, Dict[str, Any]] = {}

    def track_execution(self, result: ToolResult, context: ToolContext) -> Dict[str, Any]:
        with self._lock:
            tid = context.tenant_id
            if tid not in self._tenant_usage:
                self._tenant_usage[tid] = {
                    "total_calls": 0,
                    "external_api_calls": 0,
                    "total_duration_seconds": 0.0,
                    "total_cost": 0.0,
                    "cpu_ms": 0.0,
                    "memory_mb": 0.0,
                    "bytes_read": 0,
                    "bytes_written": 0,
                    "tool_breakdown": {},
                }

            usage = self._tenant_usage[tid]
            usage["total_calls"] += 1
            usage["total_duration_seconds"] += result.execution_time_seconds
            usage["total_cost"] += result.cost

            # Compute/storage breakdown
            cpu_ms = result.compute_usage.get("cpu_ms", 0.0)
            mem_mb = result.compute_usage.get("memory_mb", 0.0)
            usage["cpu_ms"] += cpu_ms
            usage["memory_mb"] += mem_mb

            b_read = result.storage_usage.get("bytes_read", 0)
            b_write = result.storage_usage.get("bytes_written", 0)
            usage["bytes_read"] += b_read
            usage["bytes_written"] += b_write

            # Is external call?
            if result.metadata.get("external_api_call", False):
                usage["external_api_calls"] += 1

            # Tool breakdown
            tb = usage["tool_breakdown"]
            tname = result.tool_name
            if tname not in tb:
                tb[tname] = {"calls": 0, "cost": 0.0, "duration": 0.0}
            tb[tname]["calls"] += 1
            tb[tname]["cost"] += result.cost
            tb[tname]["duration"] += result.execution_time_seconds

            logger.debug(f"[BILLING] Tenant '{tid}' tool '{tname}' billed cost=${result.cost:.4f}")
            return usage

    def get_tenant_billing_summary(self, tenant_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._tenant_usage.get(tenant_id, {
                "total_calls": 0,
                "external_api_calls": 0,
                "total_duration_seconds": 0.0,
                "total_cost": 0.0,
                "cpu_ms": 0.0,
                "memory_mb": 0.0,
                "bytes_read": 0,
                "bytes_written": 0,
                "tool_breakdown": {},
            })
