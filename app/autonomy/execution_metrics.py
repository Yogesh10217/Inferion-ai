"""
Prometheus Metrics Declarations for Autonomous Execution & Digital Workforce
"""

from prometheus_client import Counter, Gauge, Histogram

autonomous_runs_total = Counter(
    "autonomous_runs_total", "Total number of autonomous executions started", ["tenant_id", "execution_mode"]
)

autonomous_runs_active = Gauge("autonomous_runs_active", "Gauge of currently active autonomous runs", ["tenant_id"])

autonomous_runs_failed = Counter(
    "autonomous_runs_failed", "Total number of failed autonomous executions", ["tenant_id", "error_type"]
)

autonomous_runs_completed = Counter(
    "autonomous_runs_completed", "Total number of completed autonomous executions", ["tenant_id"]
)

autonomous_execution_duration_seconds = Histogram(
    "autonomous_execution_duration_seconds",
    "Duration of autonomous executions in seconds",
    ["tenant_id"],
    buckets=[0.1, 1.0, 5.0, 30.0, 60.0, 300.0, 600.0, 3600.0],
)

autonomous_checkpoints_total = Counter("autonomous_checkpoints_total", "Total checkpoints saved", ["tenant_id"])

autonomous_recoveries_total = Counter(
    "autonomous_recoveries_total", "Total checkpoint recoveries performed", ["tenant_id"]
)

autonomous_cost_total = Counter("autonomous_cost_total", "Total dollar cost incurred by autonomous runs", ["tenant_id"])
