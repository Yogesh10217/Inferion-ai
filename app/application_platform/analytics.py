"""Application Analytics Engine (Phase 5.22 - Component 10).

Measures tenant-scoped performance, user experience, and financial efficiency:
- Active users, execution volume, completion rate, fallback rate, human escalation rate,
  latency, token usage, cost per interaction, cost per outcome, user feedback, feature adoption.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ApplicationMetric(BaseModel):
    """Tenant-scoped application performance metric."""

    metric_id: str = Field(default_factory=lambda: f"met_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    metric_name: str
    metric_value: float
    dimensions: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExperienceMetric(BaseModel):
    """User experience and satisfaction metric."""

    metric_id: str = Field(default_factory=lambda: f"expmet_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    user_satisfaction_score: float = 5.0
    fallback_rate: float = 0.0
    escalation_rate: float = 0.0
    average_latency_ms: float = 0.0


class UsageInsight(BaseModel):
    """Analytical insight derived from usage patterns."""

    insight_id: str = Field(default_factory=lambda: f"ins_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    insight_type: str = "PERFORMANCE"
    summary: str
    recommendation: str = ""


class ApplicationReport(BaseModel):
    """Aggregated application analytics report."""

    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    time_window: str = "24H"
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    human_escalations: int = 0
    fallbacks_triggered: int = 0
    total_cost_usd: float = 0.0
    avg_latency_ms: float = 0.0
    insights: List[UsageInsight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApplicationAnalyticsEngine:
    """Collects & generates tenant-isolated application analytics reports."""

    def __init__(self) -> None:
        self._metrics: List[ApplicationMetric] = []

    def record_metric(
        self,
        tenant_id: str,
        application_id: str,
        metric_name: str,
        metric_value: float,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> ApplicationMetric:
        met = ApplicationMetric(
            application_id=application_id,
            tenant_id=tenant_id,
            metric_name=metric_name,
            metric_value=metric_value,
            dimensions=dimensions or {},
        )
        self._metrics.append(met)
        return met

    def generate_report(
        self,
        tenant_id: str,
        application_id: str,
        time_window: str = "24H",
    ) -> ApplicationReport:
        """Aggregate recorded metrics for an application within tenant isolation."""
        tenant_metrics = [
            m for m in self._metrics
            if m.tenant_id == tenant_id and m.application_id == application_id
        ]

        total_execs = sum(1 for m in tenant_metrics if m.metric_name == "execution_count")
        total_cost = sum(m.metric_value for m in tenant_metrics if m.metric_name == "cost_usd")
        escalations = sum(1 for m in tenant_metrics if m.metric_name == "human_escalation")
        fallbacks = sum(1 for m in tenant_metrics if m.metric_name == "fallback_triggered")

        latencies = [m.metric_value for m in tenant_metrics if m.metric_name == "latency_ms"]
        avg_lat = sum(latencies) / len(latencies) if latencies else 0.0

        insights = []
        if fallbacks > 2:
            insights.append(UsageInsight(
                application_id=application_id,
                tenant_id=tenant_id,
                insight_type="RELIABILITY",
                summary=f"Detected {fallbacks} model/agent fallbacks.",
                recommendation="Consider reviewing primary model availability or fallback thresholds.",
            ))

        return ApplicationReport(
            application_id=application_id,
            tenant_id=tenant_id,
            time_window=time_window,
            total_executions=total_execs,
            successful_executions=max(0, total_execs - fallbacks),
            human_escalations=escalations,
            fallbacks_triggered=fallbacks,
            total_cost_usd=total_cost,
            avg_latency_ms=avg_lat,
            insights=insights,
        )
