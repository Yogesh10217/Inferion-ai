"""Operational analytics generating OperationsReport, OperationsInsight, and PlatformReport primitives."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.analytics import AnalyticsMetric, AnalyticsPeriod, PlatformInsight, PlatformReport


class OperationsInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    category: str = "OPERATIONAL_STABILITY"
    title: str
    summary: str
    impact_level: str = "MEDIUM"
    platform_insight: Optional[PlatformInsight] = None


class OperationsReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    period: AnalyticsPeriod = AnalyticsPeriod.MONTHLY
    metrics: List[AnalyticsMetric] = Field(default_factory=list)
    insights: List[OperationsInsight] = Field(default_factory=list)
    platform_report: Optional[PlatformReport] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsAnalyticsEngine:
    """Produces operational analytics reports adapting to PlatformReport and PlatformInsight primitives."""

    def __init__(self) -> None:
        pass

    def generate_report(self, tenant_id: str) -> OperationsReport:
        metrics = [
            AnalyticsMetric(metric_name="total_services", metric_value=12.0),
            AnalyticsMetric(metric_name="average_assurance_score", metric_value=0.96),
            AnalyticsMetric(metric_name="open_incidents", metric_value=1.0),
            AnalyticsMetric(metric_name="detected_anomalies_30d", metric_value=4.0),
        ]

        insight = OperationsInsight(
            tenant_id=tenant_id,
            category="SERVICE_HEALTH",
            title="Service Health Stability High",
            summary="Average operational assurance score across all services remains at 0.96.",
            impact_level="LOW",
            platform_insight=PlatformInsight(
                insight_id=str(uuid.uuid4()),
                title="Service Health Stability High",
                description="Average operational assurance score across all services remains at 0.96.",
                impact_level="LOW",
            ),
        )

        p_report = PlatformReport(
            report_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            report_type="OPERATIONS_ASSURANCE_REPORT",
            period=AnalyticsPeriod.MONTHLY,
            metrics=metrics,
            insights=[insight.platform_insight] if insight.platform_insight else [],
        )

        return OperationsReport(
            tenant_id=tenant_id,
            metrics=metrics,
            insights=[insight],
            platform_report=p_report,
        )
