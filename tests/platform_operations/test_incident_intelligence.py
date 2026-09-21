"""Unit tests for Incident Intelligence Engine."""

from app.platform_operations.incident_intelligence import IncidentIntelligenceEngine


def test_incident_enrichment_and_context():
    engine = IncidentIntelligenceEngine()
    ctx = engine.create_and_enrich_incident(
        tenant_id="t1", title="Database Disconnection Incident", primary_resource_id="svc_db"
    )

    assert ctx.incident_id.startswith("inc_")
    assert ctx.incident.title == "Database Disconnection Incident"

    fetched = engine.get_incident_context(ctx.incident_id, "t1")
    assert fetched.incident_id == ctx.incident_id
