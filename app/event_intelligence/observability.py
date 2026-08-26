"""Prometheus Event Observability Subsystem (Phase 5.34)."""

import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram

from app.platform_contracts.observability import SafeMetricLabelSanitizer

logger = logging.getLogger(__name__)

EVENTS_RECEIVED_TOTAL = Counter("ai_events_received_total", "Total enterprise events received", ["category", "tenant_id"])
EVENTS_DEDUPLICATED_TOTAL = Counter("ai_events_deduplicated_total", "Total duplicate events suppressed", ["tenant_id"])
EVENTS_CORRELATED_TOTAL = Counter("ai_events_correlated_total", "Total event correlation groups formed", ["correlation_type", "tenant_id"])
EVENTS_AUTOMATION_TRIGGERED_TOTAL = Counter("ai_events_automation_triggered_total", "Total automated response plans created", ["action", "tenant_id"])
EVENTS_RESOLUTION_DURATION_SECONDS = Histogram("ai_events_resolution_duration_seconds", "Event resolution duration in seconds", ["tenant_id"])


class EventMetricsCollector:
    """Collects event intelligence metrics following standard ai_events_* conventions."""

    def record_event_received(self, category: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"category": category, "tenant_id": tenant_id})
        EVENTS_RECEIVED_TOTAL.labels(category=labels["category"], tenant_id=labels["tenant_id"]).inc()

    def record_event_deduplicated(self, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"tenant_id": tenant_id})
        EVENTS_DEDUPLICATED_TOTAL.labels(tenant_id=labels["tenant_id"]).inc()

    def record_event_correlated(self, correlation_type: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"correlation_type": correlation_type, "tenant_id": tenant_id})
        EVENTS_CORRELATED_TOTAL.labels(correlation_type=labels["correlation_type"], tenant_id=labels["tenant_id"]).inc()

    def record_automation_triggered(self, action: str, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"action": action, "tenant_id": tenant_id})
        EVENTS_AUTOMATION_TRIGGERED_TOTAL.labels(action=labels["action"], tenant_id=labels["tenant_id"]).inc()

    def record_resolution_duration(self, duration_seconds: float, tenant_id: str) -> None:
        labels = SafeMetricLabelSanitizer.sanitize_labels({"tenant_id": tenant_id})
        EVENTS_RESOLUTION_DURATION_SECONDS.labels(tenant_id=labels["tenant_id"]).observe(duration_seconds)
