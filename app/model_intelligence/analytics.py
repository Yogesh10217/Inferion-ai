"""Enterprise Model Intelligence Analytics Engine (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException
from app.platform_contracts.analytics import PlatformInsight, PlatformReport

logger = logging.getLogger(__name__)


class ModelIntelligenceInsight(BaseModel):
    insight_id: str
    category: str
    summary: str
    severity: str = "INFO"
    platform_insight: PlatformInsight


class ModelIntelligenceReport(BaseModel):
    report_id: str
    tenant_id: str
    overall_health_score: float
    total_models_monitored: int
    active_incidents_count: int
    platform_report: PlatformReport
    insights: List[ModelIntelligenceInsight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelIntelligenceAnalyticsEngine:
    """Analytics engine generating PlatformReport and PlatformInsight for model intelligence."""

    def __init__(self) -> None:
        self._reports: Dict[str, ModelIntelligenceReport] = {}

    def generate_report(
        self,
        tenant_id: str,
        total_models_monitored: int = 1,
        active_incidents_count: int = 0,
        overall_health_score: float = 95.0,
    ) -> ModelIntelligenceReport:
        rep_id = f"mrep-{uuid.uuid4().hex[:8]}"

        from app.platform_contracts.analytics import AnalyticsMetric

        p_report = PlatformReport(
            report_id=f"prep-{uuid.uuid4().hex[:6]}",
            tenant_id=tenant_id,
            report_type="MODEL_INTELLIGENCE",
            metrics=[
                AnalyticsMetric(metric_name="monitored_models", metric_value=float(total_models_monitored)),
                AnalyticsMetric(metric_name="active_incidents", metric_value=float(active_incidents_count)),
                AnalyticsMetric(metric_name="health_score", metric_value=float(overall_health_score)),
            ],
        )

        pinsight = PlatformInsight(
            insight_id=f"pins-{uuid.uuid4().hex[:6]}",
            title="Model Assurance Summary",
            description=f"Monitoring {total_models_monitored} models with {active_incidents_count} active incidents.",
            impact_level="LOW" if active_incidents_count == 0 else "HIGH",
        )

        insight = ModelIntelligenceInsight(
            insight_id=f"mins-{uuid.uuid4().hex[:6]}",
            category="model_assurance",
            summary=f"Health Score: {overall_health_score:.1f}%",
            severity="INFO" if active_incidents_count == 0 else "WARNING",
            platform_insight=pinsight,
        )

        report = ModelIntelligenceReport(
            report_id=rep_id,
            tenant_id=tenant_id,
            overall_health_score=overall_health_score,
            total_models_monitored=total_models_monitored,
            active_incidents_count=active_incidents_count,
            platform_report=p_report,
            insights=[insight],
        )

        self._reports[rep_id] = report
        logger.info(f"[MODEL ANALYTICS] Generated report {rep_id} for tenant {tenant_id}")
        return report

    def get_report(self, report_id: str, tenant_id: str) -> ModelIntelligenceReport:
        rep = self._reports.get(report_id)
        if not rep:
            raise ValueError(f"Report '{report_id}' not found.")
        if rep.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return rep
