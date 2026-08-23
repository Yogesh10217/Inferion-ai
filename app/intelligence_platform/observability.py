"""Prometheus Observability Metrics Collector for Intelligence Platform."""

import logging
from typing import Dict, Any, Optional

try:
    from prometheus_client import Counter, Gauge, Histogram

    SIGNALS_TOTAL = Counter("ai_intelligence_signals_total", "Total intelligence signals ingested", ["tenant_id", "source"])
    INSIGHTS_TOTAL = Counter("ai_intelligence_insights_total", "Total insights generated", ["tenant_id", "insight_type"])
    RECOMMENDATIONS_TOTAL = Counter("ai_intelligence_recommendations_total", "Total recommendations generated", ["tenant_id", "recommendation_type"])
    DECISIONS_TOTAL = Counter("ai_intelligence_decisions_total", "Total decisions processed", ["tenant_id", "status"])
    EXECUTION_TOTAL = Counter("ai_intelligence_execution_total", "Total executions delegated", ["tenant_id", "target"])
    HUMAN_OVERRIDES_TOTAL = Counter("ai_intelligence_human_overrides_total", "Total human overrides/rejections", ["tenant_id"])
    FORECAST_ACCURACY = Gauge("ai_intelligence_forecast_accuracy", "Forecast accuracy percentage", ["tenant_id"])
    OPTIMIZATION_SAVINGS = Gauge("ai_intelligence_optimization_savings", "Cumulative optimization savings in USD", ["tenant_id"])
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class IntelligenceMetricsCollector:
    """Collects operational metrics for Intelligence Platform."""

    def record_signal(self, tenant_id: str, source: str) -> None:
        if PROMETHEUS_AVAILABLE:
            SIGNALS_TOTAL.labels(tenant_id=tenant_id, source=source).inc()

    def record_insight(self, tenant_id: str, insight_type: str) -> None:
        if PROMETHEUS_AVAILABLE:
            INSIGHTS_TOTAL.labels(tenant_id=tenant_id, insight_type=insight_type).inc()

    def record_recommendation(self, tenant_id: str, recommendation_type: str) -> None:
        if PROMETHEUS_AVAILABLE:
            RECOMMENDATIONS_TOTAL.labels(tenant_id=tenant_id, recommendation_type=recommendation_type).inc()

    def record_decision(self, tenant_id: str, status: str) -> None:
        if PROMETHEUS_AVAILABLE:
            DECISIONS_TOTAL.labels(tenant_id=tenant_id, status=status).inc()

    def record_execution(self, tenant_id: str, target: str) -> None:
        if PROMETHEUS_AVAILABLE:
            EXECUTION_TOTAL.labels(tenant_id=tenant_id, target=target).inc()

    def record_override(self, tenant_id: str) -> None:
        if PROMETHEUS_AVAILABLE:
            HUMAN_OVERRIDES_TOTAL.labels(tenant_id=tenant_id).inc()

    def record_forecast_accuracy(self, tenant_id: str, accuracy_pct: float) -> None:
        if PROMETHEUS_AVAILABLE:
            FORECAST_ACCURACY.labels(tenant_id=tenant_id).set(accuracy_pct)

    def record_savings(self, tenant_id: str, amount_usd: float) -> None:
        if PROMETHEUS_AVAILABLE:
            OPTIMIZATION_SAVINGS.labels(tenant_id=tenant_id).set(amount_usd)
