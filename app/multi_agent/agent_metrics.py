"""
Prometheus Metrics Declarations for Multi-Agent Platform
"""

from prometheus_client import Counter, Gauge, Histogram

agent_team_runs_total = Counter(
    "agent_team_runs_total",
    "Total number of team execution runs",
    ["team_id", "team_type", "tenant_id"]
)

agent_team_failures_total = Counter(
    "agent_team_failures_total",
    "Total number of team execution failures",
    ["team_id", "error_type", "tenant_id"]
)

agent_messages_total = Counter(
    "agent_messages_total",
    "Total number of agent-to-agent messages sent",
    ["message_type", "team_id"]
)

agent_delegations_total = Counter(
    "agent_delegations_total",
    "Total number of task delegations",
    ["strategy", "team_id"]
)

agent_consensus_total = Counter(
    "agent_consensus_total",
    "Total consensus evaluations",
    ["strategy", "result"]
)

agent_negotiations_total = Counter(
    "agent_negotiations_total",
    "Total negotiation sessions conducted",
    ["team_id", "status"]
)

agent_handoffs_total = Counter(
    "agent_handoffs_total",
    "Total state handoffs executed between agents",
    ["team_id"]
)

agent_team_duration_seconds = Histogram(
    "agent_team_duration_seconds",
    "Histogram of team execution duration in seconds",
    ["team_id", "tenant_id"],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

agent_team_success_rate = Gauge(
    "agent_team_success_rate",
    "Success rate gauge for agent team executions",
    ["team_id"]
)

agent_team_failure_rate = Gauge(
    "agent_team_failure_rate",
    "Failure rate gauge for agent team executions",
    ["team_id"]
)
