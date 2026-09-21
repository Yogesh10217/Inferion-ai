"""Unit tests for Intelligence Analytics Engine."""

from app.intelligence_platform.analytics import IntelligenceAnalyticsEngine


def test_intelligence_report_generation():
    engine = IntelligenceAnalyticsEngine()
    rep = engine.generate_report(
        "t1", insights_generated=10, recommendations_generated=8, recommendations_accepted=8, savings_usd=250.0
    )

    assert rep.report_id.startswith("rep_")
    assert rep.insights_generated == 10
    assert rep.optimizations.total_estimated_savings_usd == 250.0
