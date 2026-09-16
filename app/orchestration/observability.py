"""Process Orchestration Prometheus Metrics Collector."""

import logging

try:
    from prometheus_client import Counter, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

if PROMETHEUS_AVAILABLE:
    ORCH_EXECUTIONS_TOTAL = Counter("ai_orchestration_workflow_executions_total", "Total workflow executions", ["tenant_id", "status"])
    ORCH_DURATION_SECONDS = Histogram("ai_orchestration_workflow_duration_seconds", "Workflow duration seconds", ["tenant_id"])
    ORCH_FAILURES_TOTAL = Counter("ai_orchestration_step_failures_total", "Total step failures", ["tenant_id"])
    ORCH_HUMAN_TASKS_TOTAL = Counter("ai_orchestration_human_tasks_total", "Total human tasks", ["tenant_id", "status"])
    ORCH_CASES_TOTAL = Counter("ai_orchestration_cases_total", "Total enterprise cases", ["tenant_id", "status"])
    ORCH_COMPENSATIONS_TOTAL = Counter("ai_orchestration_compensations_total", "Total saga compensations", ["tenant_id"])


class OrchestrationMetricsCollector:
    """Collects Prometheus metrics for the Orchestration Platform."""

    def record_execution(self, tenant_id: str, status: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                ORCH_EXECUTIONS_TOTAL.labels(tenant_id=tenant_id, status=status).inc()
            except Exception:
                pass

    def record_human_task(self, tenant_id: str, status: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                ORCH_HUMAN_TASKS_TOTAL.labels(tenant_id=tenant_id, status=status).inc()
            except Exception:
                pass
