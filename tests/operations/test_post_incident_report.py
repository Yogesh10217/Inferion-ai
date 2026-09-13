from app.operations.incident_management import IncidentManager, IncidentSeverity
from app.operations.post_incident import PostIncidentReportGenerator


def test_post_incident_report_generation():
    mgr = IncidentManager()
    inc = mgr.create_incident("P2 Major Outage", IncidentSeverity.P2, summary="Secret password123 leaked")
    gen = PostIncidentReportGenerator()
    report = gen.generate_report(inc, root_cause="Memory leak with password123 in logs")

    assert report.incident_id == inc.incident_id
    assert report.severity == "P2"
    # Secret sanitization check
    assert "password123" not in report.root_cause
    assert "[REDACTED:" in report.root_cause
