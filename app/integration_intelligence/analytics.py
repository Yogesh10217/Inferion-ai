"""Integration Analytics Engine (Phase 5.40)."""

import uuid
from typing import List

from pydantic import BaseModel, Field

from app.platform_contracts.analytics import (
    AnalyticsMetric,
    AnalyticsPeriod,
    PlatformInsight,
    PlatformReport,
)


class IntegrationInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"int_ins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    impact_level: str = "MEDIUM"


class IntegrationAnalyticsEngine:
    """Generates tenant integration analytics and adapts results to PlatformReport."""

    def generate_report(
        self,
        tenant_id: str,
        active_connectors_count: int = 0,
        active_workflows_count: int = 0,
        execution_success_rate: float = 100.0,
        failure_count: int = 0,
        retry_count: int = 0,
        verification_failure_count: int = 0,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
    ) -> PlatformReport:
        int_insights: List[IntegrationInsight] = []
        plat_insights: List[PlatformInsight] = []

        if failure_count > 0:
            ins = IntegrationInsight(
                title="Integration Failures Detected",
                description=f"{failure_count} workflow execution failures recorded.",
                impact_level="HIGH",
            )
            int_insights.append(ins)
            plat_insights.append(
                PlatformInsight(title=ins.title, description=ins.description, impact_level=ins.impact_level)
            )

        if verification_failure_count > 0:
            ins = IntegrationInsight(
                title="Verification Failures Identified",
                description=f"{verification_failure_count} external outcome verifications failed.",
                impact_level="MEDIUM",
            )
            int_insights.append(ins)
            plat_insights.append(
                PlatformInsight(title=ins.title, description=ins.description, impact_level=ins.impact_level)
            )

        metrics = [
            AnalyticsMetric(metric_name="active_connectors_count", metric_value=float(active_connectors_count)),
            AnalyticsMetric(metric_name="active_workflows_count", metric_value=float(active_workflows_count)),
            AnalyticsMetric(metric_name="execution_success_rate", metric_value=execution_success_rate),
            AnalyticsMetric(metric_name="failure_count", metric_value=float(failure_count)),
            AnalyticsMetric(metric_name="retry_count", metric_value=float(retry_count)),
            AnalyticsMetric(metric_name="verification_failure_count", metric_value=float(verification_failure_count)),
        ]

        report = PlatformReport(
            tenant_id=tenant_id,
            report_type="INTEGRATION_INTELLIGENCE",
            period=period,
            metrics=metrics,
            insights=plat_insights,
        )
        return report
