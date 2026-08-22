"""Extension Observability Tracing & Metrics Collector."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExtensionTraceContext(BaseModel):
    """Distributed tracing context propagated across extension execution boundaries."""

    trace_id: str
    span_id: str
    execution_id: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    developer_id: Optional[str] = None
    project_id: Optional[str] = None
    extension_id: str
    extension_version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExtensionMetricsCollector:
    """Prometheus metrics mapper for extensions."""

    def __init__(self) -> None:
        self.metrics: Dict[str, float] = {
            "extensions_installed_total": 0.0,
            "extensions_enabled_total": 0.0,
            "extension_executions_total": 0.0,
            "extension_failures_total": 0.0,
            "extension_duration_seconds": 0.0,
            "extension_cost_total": 0.0,
            "extension_upgrade_total": 0.0,
            "extension_rollbacks_total": 0.0,
            "extension_security_blocks_total": 0.0,
        }

    def increment(self, metric_name: str, value: float = 1.0) -> None:
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
        else:
            self.metrics[metric_name] = value

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self.metrics)
