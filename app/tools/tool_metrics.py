"""
Prometheus Metrics Declarations for Enterprise Tool Calling Subsystem
"""

from prometheus_client import Counter, Histogram, Gauge

tool_calls_total = Counter(
    "tool_calls_total",
    "Total number of tool calls executed",
    ["tool_name", "status", "tenant_id"]
)

tool_failures_total = Counter(
    "tool_failures_total",
    "Total number of tool execution failures",
    ["tool_name", "error_type", "tenant_id"]
)

tool_duration_seconds = Histogram(
    "tool_duration_seconds",
    "Histogram of tool execution duration in seconds",
    ["tool_name", "tenant_id"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

tool_cost_total = Counter(
    "tool_cost_total",
    "Total financial cost attributed to tool executions in USD",
    ["tool_name", "tenant_id"]
)

tool_active_executions = Gauge(
    "tool_active_executions",
    "Number of active in-flight tool executions",
    ["tool_name"]
)
