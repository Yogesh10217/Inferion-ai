"""Unit tests for Operational Learning & Post-Incident Insight Engine."""

from app.platform_operations.learning import OperationalLearningManager, PreventionRule


def test_post_incident_insight_generation():
    mgr = OperationalLearningManager()
    rule = PreventionRule(name="Block Unverified Canary Deployment", condition="latency > 2000ms", action="BLOCK")

    insight = mgr.generate_post_incident_insight(
        tenant_id="t1",
        incident_id="inc_404",
        title="Canary Deployment Memory Leak",
        summary="Memory leak in v2.4",
        root_cause_summary="Buffer unallocated in connection pool",
        prevention_rules=[rule],
    )

    assert insight.insight_id.startswith("ins_")
    assert len(insight.prevention_rules) == 1

    insights = mgr.list_insights("t1")
    assert len(insights) >= 1
