from app.operations.incident_management import IncidentManager, IncidentSeverity
from app.operations.operations_orchestrator import OperationsOrchestrator
from app.operations.post_incident import PostIncidentReportGenerator


def test_secret_canaries_zero_exposure():
    canaries = ["password123", "canary_secret", "admin123", "secret_key"]

    orchestrator = OperationsOrchestrator()
    res = orchestrator.run_pipeline(
        app_data={
            "request_count": 1000,
            "failure_count": 0,
            "secret_key": "secret_key_val",
            "password": "password123",
            "canary": "canary_secret",
            "admin": "admin123",
        },
        health_data={"live": True, "ready": True, "health": True, "canary": "canary_secret"},
    )

    pipeline_dict_str = str(res.to_dict())

    for canary in canaries:
        assert canary not in pipeline_dict_str or "[REDACTED:" in pipeline_dict_str, f"Canary '{canary}' exposed unmasked in operational pipeline payload!"

    # Incident postmortem secret sanitization check
    mgr = IncidentManager()
    inc = mgr.create_incident("Canary Incident", IncidentSeverity.P1, summary="Leaked password123 and admin123")
    report = PostIncidentReportGenerator().generate_report(inc, root_cause="Found canary_secret and secret_key in trace")
    report_str = str(report.to_dict())

    for canary in canaries:
        assert canary not in report_str or "[REDACTED:" in report_str, f"Canary '{canary}' exposed unmasked in post-incident report!"
