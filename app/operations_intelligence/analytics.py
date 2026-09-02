"""Operations Analytics Engine (Phase 5.41)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException
from app.platform_contracts.analytics import (
    PlatformReport,
    PlatformInsight,
    AnalyticsMetric,
    AnalyticsPeriod,
)


class OperationsInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"op_ins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    impact_level: str = "MEDIUM"


OperationsReport = PlatformReport


class OperationsAnalyticsEngine:
    """Generates tenant operational analytics and adapts results to PlatformReport."""

    def generate_report(
        self,
        tenant_id: str,
        active_services_count: int = 0,
        open_incidents_count: int = 0,
        major_incidents_count: int = 0,
        mttr_minutes: float = 15.0,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
    ) -> PlatformReport:
        op_insights: List[OperationsInsight] = []
        plat_insights: List[PlatformInsight] = []

        if major_incidents_count > 0:
            ins = OperationsInsight(
                title="Major Incident Alert",
                description=f"{major_incidents_count} major incidents declared during reporting period.",
                impact_level="CRITICAL",
            )
            op_insights.append(ins)
            plat_insights.append(PlatformInsight(title=ins.title, description=ins.description, impact_level=ins.impact_level))

        metrics = [
            AnalyticsMetric(metric_name="active_services_count", metric_value=float(active_services_count)),
            AnalyticsMetric(metric_name="open_incidents_count", metric_value=float(open_incidents_count)),
            AnalyticsMetric(metric_name="major_incidents_count", metric_value=float(major_incidents_count)),
            AnalyticsMetric(metric_name="mttr_minutes", metric_value=mttr_minutes),
        ]

        report = PlatformReport(
            tenant_id=tenant_id,
            report_type="OPERATIONS_INTELLIGENCE",
            period=period,
            metrics=metrics,
            insights=plat_insights,
        )
        return report
