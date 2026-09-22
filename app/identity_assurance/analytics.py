"""Identity Assurance Analytics Engine."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException
from app.platform_contracts.analytics import AnalyticsMetric, AnalyticsPeriod, PlatformReport


class IdentityAssuranceInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    category: str  # TRUST, PRIVILEGE, ANOMALY, REVIEW
    summary: str
    impact_score: float = 0.5
    recommendations: List[str] = Field(default_factory=list)


class IdentityAssuranceReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    period: str = "LAST_30_DAYS"
    total_identities_assessed: int = 100
    avg_trust_score: float = 0.88
    total_anomalies_detected: int = 2
    high_privilege_identities_count: int = 5
    insights: List[IdentityAssuranceInsight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityAssuranceAnalyticsEngine:
    """Produces identity assurance reports and insights using platform analytics primitives."""

    def __init__(self) -> None:
        self._reports: Dict[str, IdentityAssuranceReport] = {}

    def generate_report(self, tenant_id: str) -> IdentityAssuranceReport:
        insight = IdentityAssuranceInsight(
            tenant_id=tenant_id,
            category="PRIVILEGE",
            summary="High privilege concentration detected in 5 service accounts.",
            impact_score=0.7,
            recommendations=["Initiate privileged access review"],
        )
        report = IdentityAssuranceReport(
            tenant_id=tenant_id,
            insights=[insight],
        )
        self._reports[report.report_id] = report
        return report

    def get_report(self, tenant_id: str, report_id: str) -> IdentityAssuranceReport:
        report = self._reports.get(report_id)
        if not report or report.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return report

    def to_platform_report(self, report: IdentityAssuranceReport) -> PlatformReport:
        metrics = [
            AnalyticsMetric(metric_name="total_identities", metric_value=float(report.total_identities_assessed)),
            AnalyticsMetric(metric_name="avg_trust_score", metric_value=report.avg_trust_score),
            AnalyticsMetric(metric_name="anomalies_count", metric_value=float(report.total_anomalies_detected)),
        ]
        return PlatformReport(
            tenant_id=report.tenant_id,
            report_type="IDENTITY_ASSURANCE",
            period=AnalyticsPeriod.MONTHLY,
            metrics=metrics,
        )
