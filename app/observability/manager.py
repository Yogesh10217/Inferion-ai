"""Unified Observability Manager coordinating tracing, logging, cost, performance, replay, failure, anomaly, SLA, alerting, and evaluation."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from app.observability.alerting import AlertManager
from app.observability.anomaly_detection import AnomalyDetector
from app.observability.context import ObservabilityContext, get_current_context, set_current_context
from app.observability.cost_tracking import CostTracker
from app.observability.evaluation import EvaluationEngine
from app.observability.execution_trace import ExecutionTrace
from app.observability.failure_analysis import FailureAnalyzer
from app.observability.logging import StructuredLogger
from app.observability.metrics import get_observability_metrics
from app.observability.performance import PerformanceMonitor
from app.observability.replay import ExecutionReplayManager
from app.observability.sla import SLAEngine
from app.observability.tracing import TracingManager

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """Unified coordinator for the Enterprise AI Observability, Monitoring & AIOps Platform."""

    def __init__(
        self,
        event_bus: Optional[Any] = None,
        pricing_service: Optional[Any] = None,
        session_factory: Optional[Any] = None,
    ) -> None:
        self.session_factory = session_factory
        self.tracing = TracingManager()
        self.logger = StructuredLogger(service_name="llm-inference-engine", component="manager")
        self.cost_tracker = CostTracker(pricing_service=pricing_service)
        self.performance = PerformanceMonitor()
        self.replay_manager = ExecutionReplayManager()
        self.failure_analyzer = FailureAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.sla_engine = SLAEngine()
        self.alert_manager = AlertManager(event_bus=event_bus)
        self.evaluation_engine = EvaluationEngine()
        self.metrics = get_observability_metrics()

    def create_context(
        self,
        trace_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        tool_execution_id: Optional[str] = None,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> ObservabilityContext:
        """Create and populate a new ObservabilityContext."""
        ctx = ObservabilityContext(
            trace_id=trace_id or get_current_context().trace_id,
            execution_id=execution_id or trace_id or get_current_context().execution_id,
            tenant_id=tenant_id or get_current_context().tenant_id,
            workspace_id=workspace_id or get_current_context().workspace_id,
            organization_id=organization_id or get_current_context().organization_id,
            user_id=user_id or get_current_context().user_id,
            agent_id=agent_id or get_current_context().agent_id,
            workflow_id=workflow_id or get_current_context().workflow_id,
            worker_id=worker_id or get_current_context().worker_id,
            tool_execution_id=tool_execution_id or get_current_context().tool_execution_id,
            model_id=model_id or get_current_context().model_id,
            provider=provider or get_current_context().provider,
        )
        set_current_context(ctx)
        return ctx

    def start_execution(
        self,
        component: str,
        name: str,
        context: Optional[ObservabilityContext] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start tracking an execution span and record performance/concurrency state."""
        ctx = context or get_current_context()
        span_dict = self.tracing.start_trace(name=name, context=ctx, attributes=attributes)
        self.performance.increment_concurrency(component)
        self.metrics.ai_active_executions.labels(component=component).inc()
        self.metrics.ai_execution_total.labels(component=component).inc()
        return span_dict

    def end_execution(
        self,
        span_or_id: Any,
        component: str,
        status: str = "OK",
        latency_ms: Optional[float] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        model: str = "default",
        provider: str = "default",
        error: Optional[Exception] = None,
        context: Optional[ObservabilityContext] = None,
    ) -> Dict[str, Any]:
        """End tracking an execution span, record cost, performance, anomalies, and metrics."""
        ctx = context or get_current_context()

        attrs: Dict[str, Any] = {
            "component": component,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }

        # Record token cost if tokens used
        if input_tokens > 0 or output_tokens > 0:
            rec = self.cost_tracker.record_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                provider=provider,
                context=ctx,
            )
            attrs["cost"] = rec.cost
            self.metrics.ai_tokens_total.labels(type="input", model=model).inc(input_tokens)
            self.metrics.ai_tokens_total.labels(type="output", model=model).inc(output_tokens)
            self.metrics.ai_cost_total.labels(tenant_id=ctx.tenant_id or "default", model=model).inc(rec.cost)

        span_dict = self.tracing.end_span(span_or_id, status=status, attributes=attrs)

        if error:
            self.tracing.record_exception(span_or_id, error)

        dur_ms = latency_ms if latency_ms is not None else span_dict.get("duration_ms", 0.0)
        is_error = status.upper() in ["ERROR", "FAILED"] or error is not None

        # Record performance
        self.performance.record_latency(component, dur_ms, is_error=is_error)
        self.performance.decrement_concurrency(component)
        self.metrics.ai_active_executions.labels(component=component).dec()
        self.metrics.ai_execution_duration_seconds.labels(component=component).observe(dur_ms / 1000.0)

        if is_error:
            cat = self.failure_analyzer.identify_root_cause(str(error) if error else "Execution error", component)
            self.metrics.ai_execution_failures_total.labels(component=component, failure_category=cat).inc()

        # Anomaly detection check
        anomalies = self.anomaly_detector.detect_anomalies(component, latency_ms=dur_ms, error_rate=0.0)
        for a in anomalies:
            self.metrics.ai_anomalies_total.labels(anomaly_type=a.anomaly_type, component=component).inc()

        return span_dict

    def get_execution_timeline(self, trace_id: str) -> Dict[str, Any]:
        """Construct full execution tree and timeline graph for a trace."""
        raw_spans = self.tracing.get_trace(trace_id)
        exec_trace = ExecutionTrace(trace_id=trace_id)
        exec_trace.build_tree(raw_spans)
        return exec_trace.to_dict()

    def get_operations_status(self) -> Dict[str, Any]:
        """Get operational status across platform components."""
        perf_data = self.performance.get_all_performance()
        total_alerts = len(self.alert_manager.get_alerts(status="FIRING"))
        slo_statuses = self.sla_engine.get_all_slo_statuses()
        violated_slos = [s for s in slo_statuses if s.get("status") == "VIOLATED"]

        system_health = "HEALTHY"
        if total_alerts > 0 or len(violated_slos) > 0:
            system_health = "DEGRADED"
        if any(s.get("level") == "CRITICAL" for s in self.alert_manager.get_alerts(status="FIRING")):
            system_health = "UNHEALTHY"

        return {
            "status": system_health,
            "timestamp": time.time(),
            "active_alerts_firing": total_alerts,
            "violated_slos_count": len(violated_slos),
            "components_monitored": len(perf_data),
            "performance_summary": perf_data,
        }

    def get_operations_dashboard(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get aggregated executive AIOps dashboard payload."""
        status = self.get_operations_status()
        costs = self.cost_tracker.get_cost_breakdown(tenant_id=tenant_id)
        alerts = self.alert_manager.get_alerts(tenant_id=tenant_id)
        anomalies = self.anomaly_detector.get_recent_anomalies(limit=20)
        slos = self.sla_engine.get_all_slo_statuses(tenant_id=tenant_id)

        return {
            "status": status["status"],
            "timestamp": time.time(),
            "cost_summary": {
                "total_cost": costs["total_cost"],
                "total_tokens": costs["total_tokens"],
            },
            "performance_by_component": status["performance_summary"],
            "alerts": alerts[:10],
            "recent_anomalies": anomalies,
            "slos": slos,
        }
