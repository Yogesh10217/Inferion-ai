"""Enterprise decision analytics reporting reusing PlatformReport and PlatformInsight primitives."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.platform_contracts.analytics import AnalyticsMetric, AnalyticsPeriod, PlatformInsight, PlatformReport

DecisionInsight = PlatformInsight


class DecisionTrend(BaseModel):
    metric_name: str
    historical_values: List[float] = Field(default_factory=list)
    trend_direction: str = "STABLE"  # INCREASING, DECREASING, STABLE


class DecisionAnalyticsReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    total_decisions_analyzed: int = 0
    decisions_by_status: Dict[str, int] = Field(default_factory=dict)
    decisions_by_outcome: Dict[str, int] = Field(default_factory=dict)
    average_confidence_score: float = 0.0
    average_risk_score: float = 0.0
    insights: List[PlatformInsight] = Field(default_factory=list)
    report_ref: PlatformReport
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionGovernanceAnalyticsEngine:
    """Generates analytics reports and strategic insights for decision governance."""

    def __init__(self) -> None:
        self._reports: Dict[str, DecisionAnalyticsReport] = {}

    def generate_analytics_report(
        self,
        tenant_id: str,
        decisions: List[Any],
    ) -> DecisionAnalyticsReport:
        status_counts: Dict[str, int] = {}
        outcome_counts: Dict[str, int] = {}
        total_conf = 0.0
        total_risk = 0.0

        for d in decisions:
            st = getattr(d, "status", "UNKNOWN")
            st_val = str(getattr(st, "value", st))
            status_counts[st_val] = status_counts.get(st_val, 0) + 1

            oc = getattr(d, "outcome", None)
            if oc:
                oc_val = str(getattr(oc, "value", oc))
                outcome_counts[oc_val] = outcome_counts.get(oc_val, 0) + 1

            total_conf += getattr(d, "confidence", 0.85)
            total_risk += getattr(d, "risk_score", 0.20)

        n = len(decisions)
        avg_conf = total_conf / n if n > 0 else 0.85
        avg_risk = total_risk / n if n > 0 else 0.20

        p_insight = PlatformInsight(
            title="High Decision Confidence Observed",
            description=f"Average decision confidence score across {n} decisions is {avg_conf:.2f}.",
            impact_level="MEDIUM",
        )

        metrics_list = [
            AnalyticsMetric(metric_name="total_decisions", metric_value=float(n)),
            AnalyticsMetric(metric_name="average_confidence", metric_value=avg_conf),
            AnalyticsMetric(metric_name="average_risk", metric_value=avg_risk),
        ]

        p_report = PlatformReport(
            tenant_id=tenant_id,
            report_type="DECISION_GOVERNANCE_SUMMARY",
            period=AnalyticsPeriod.DAILY,
            metrics=metrics_list,
            insights=[p_insight],
        )

        report = DecisionAnalyticsReport(
            tenant_id=tenant_id,
            total_decisions_analyzed=n,
            decisions_by_status=status_counts,
            decisions_by_outcome=outcome_counts,
            average_confidence_score=avg_conf,
            average_risk_score=avg_risk,
            insights=[p_insight],
            report_ref=p_report,
        )
        self._reports[report.report_id] = report
        return report
