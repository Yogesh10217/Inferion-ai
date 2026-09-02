"""Enterprise Financial Analytics (Phase 5.42)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException
from app.platform_contracts.analytics import (
    PlatformReport,
    PlatformInsight,
    AnalyticsMetric,
    AnalyticsPeriod,
)


class FinOpsInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"fin_ins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    impact_level: str = "MEDIUM"


FinOpsReport = PlatformReport


class FinOpsAnalyticsEngine:
    """Generates tenant financial analytics and adapts results to PlatformReport."""

    def generate_report(
        self,
        tenant_id: str,
        total_spend_usd: float = 0.0,
        budget_utilization_pct: float = 0.0,
        anomalies_count: int = 0,
        potential_savings_usd: float = 0.0,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
    ) -> PlatformReport:
        op_insights: List[FinOpsInsight] = []
        plat_insights: List[PlatformInsight] = []

        if anomalies_count > 0:
            ins = FinOpsInsight(
                title="Cost Anomaly Alert",
                description=f"{anomalies_count} financial anomalies detected during period.",
                impact_level="HIGH",
            )
            op_insights.append(ins)
            plat_insights.append(PlatformInsight(title=ins.title, description=ins.description, impact_level=ins.impact_level))

        metrics = [
            AnalyticsMetric(metric_name="total_spend_usd", metric_value=total_spend_usd),
            AnalyticsMetric(metric_name="budget_utilization_pct", metric_value=budget_utilization_pct),
            AnalyticsMetric(metric_name="anomalies_count", metric_value=float(anomalies_count)),
            AnalyticsMetric(metric_name="potential_savings_usd", metric_value=potential_savings_usd),
        ]

        report = PlatformReport(
            tenant_id=tenant_id,
            report_type="FINOPS_INTELLIGENCE",
            period=period,
            metrics=metrics,
            insights=plat_insights,
        )
        return report
