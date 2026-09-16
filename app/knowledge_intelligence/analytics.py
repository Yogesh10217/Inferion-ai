"""Knowledge Analytics Engine Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.platform_contracts.analytics import (
    AnalyticsDimension,
    AnalyticsMetric,
    AnalyticsPeriod,
    PlatformInsight,
    PlatformReport,
)


class KnowledgeInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"kinsight_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    impact_level: str = "MEDIUM"


class KnowledgeReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"kreport_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    report_type: str = "KNOWLEDGE_INTELLIGENCE_SUMMARY"
    metrics: List[AnalyticsMetric] = Field(default_factory=list)
    insights: List[PlatformInsight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeAnalyticsEngine:
    """Generates tenant-scoped knowledge intelligence analytics reports and insights."""

    def generate_report(
        self,
        tenant_id: str,
        total_items: int = 0,
        stale_count: int = 0,
        contradiction_count: int = 0,
    ) -> PlatformReport:
        m1 = AnalyticsMetric(
            metric_name="total_knowledge_items",
            metric_value=float(total_items),
            dimensions=[AnalyticsDimension(dimension_name="tenant_id", dimension_value=tenant_id)],
        )
        m2 = AnalyticsMetric(
            metric_name="stale_knowledge_ratio",
            metric_value=float(stale_count / total_items) if total_items > 0 else 0.0,
            dimensions=[AnalyticsDimension(dimension_name="tenant_id", dimension_value=tenant_id)],
        )
        m3 = AnalyticsMetric(
            metric_name="contradiction_count",
            metric_value=float(contradiction_count),
            dimensions=[AnalyticsDimension(dimension_name="tenant_id", dimension_value=tenant_id)],
        )

        insights = []
        if stale_count > 0:
            insights.append(
                PlatformInsight(
                    title="Stale Knowledge Detected",
                    description=f"{stale_count} knowledge items require revalidation.",
                    impact_level="MEDIUM",
                )
            )
        if contradiction_count > 0:
            insights.append(
                PlatformInsight(
                    title="Knowledge Conflicts Present",
                    description=f"{contradiction_count} contradictions need governance resolution.",
                    impact_level="HIGH",
                )
            )

        return PlatformReport(
            tenant_id=tenant_id,
            report_type="KNOWLEDGE_INTELLIGENCE_ANALYTICS",
            period=AnalyticsPeriod.DAILY,
            metrics=[m1, m2, m3],
            insights=insights,
        )
