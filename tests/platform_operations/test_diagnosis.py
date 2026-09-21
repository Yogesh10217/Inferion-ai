"""Unit tests for Evidence-Backed Root Cause Analyzer."""

from app.platform_operations.diagnosis import RootCauseAnalyzer
from app.platform_operations.incident_intelligence import IncidentIntelligenceEngine


def test_deployment_regression_diagnosis_hypothesis():
    engine = IncidentIntelligenceEngine()
    analyzer = RootCauseAnalyzer()

    ctx = engine.create_and_enrich_incident(
        tenant_id="t1",
        title="Latency Surge Post Deployment",
        recent_deployments=[{"version_id": "v2.1.0"}],
    )

    diag = analyzer.diagnose_incident("t1", ctx)
    assert diag.top_hypothesis is not None
    assert diag.top_hypothesis.category == "DEPLOYMENT_REGRESSION"
    assert "ROLLBACK" in diag.top_hypothesis.suggested_remediations
