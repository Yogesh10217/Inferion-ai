"""Access Intelligence Analytics Engine (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.platform_contracts.analytics import (
    AnalyticsMetric,
    AnalyticsPeriod,
    PlatformInsight,
    PlatformReport,
)


class AccessInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"acc_ins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    impact_level: str = "MEDIUM"


class AccessReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"acc_rep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    privileged_identities_count: int = 0
    excessive_entitlements_count: int = 0
    toxic_combinations_count: int = 0
    anomalous_access_events_count: int = 0
    certification_completion_rate: float = 100.0
    remediation_success_rate: float = 100.0
    average_risk_score: float = 20.0
    insights: List[AccessInsight] = Field(default_factory=list)


class AccessAnalyticsEngine:
    """Generates tenant access intelligence analytics and adapts results to PlatformReport."""

    def generate_report(
        self,
        tenant_id: str,
        privileged_identities_count: int = 0,
        excessive_entitlements_count: int = 0,
        toxic_combinations_count: int = 0,
        anomalous_access_events_count: int = 0,
        certification_completion_rate: float = 100.0,
        remediation_success_rate: float = 100.0,
        average_risk_score: float = 20.0,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
    ) -> PlatformReport:
        acc_insights: List[AccessInsight] = []
        plat_insights: List[PlatformInsight] = []

        if toxic_combinations_count > 0:
            ins = AccessInsight(
                title="Toxic Combinations Detected",
                description=f"{toxic_combinations_count} segregation of duties violations require remediation.",
                impact_level="HIGH",
            )
            acc_insights.append(ins)
            plat_insights.append(PlatformInsight(title=ins.title, description=ins.description, impact_level=ins.impact_level))

        if excessive_entitlements_count > 0:
            ins = AccessInsight(
                title="Excessive Entitlements Identified",
                description=f"{excessive_entitlements_count} unneeded or unused permissions detected across identities.",
                impact_level="MEDIUM",
            )
            acc_insights.append(ins)
            plat_insights.append(PlatformInsight(title=ins.title, description=ins.description, impact_level=ins.impact_level))

        metrics = [
            AnalyticsMetric(metric_name="privileged_identities_count", metric_value=float(privileged_identities_count)),
            AnalyticsMetric(metric_name="excessive_entitlements_count", metric_value=float(excessive_entitlements_count)),
            AnalyticsMetric(metric_name="toxic_combinations_count", metric_value=float(toxic_combinations_count)),
            AnalyticsMetric(metric_name="anomalous_access_events_count", metric_value=float(anomalous_access_events_count)),
            AnalyticsMetric(metric_name="certification_completion_rate", metric_value=certification_completion_rate),
            AnalyticsMetric(metric_name="remediation_success_rate", metric_value=remediation_success_rate),
            AnalyticsMetric(metric_name="average_risk_score", metric_value=average_risk_score),
        ]

        report = PlatformReport(
            tenant_id=tenant_id,
            report_type="ACCESS_INTELLIGENCE",
            period=period,
            metrics=metrics,
            insights=plat_insights,
        )
        return report
