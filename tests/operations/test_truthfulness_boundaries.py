from app.operations.operations_orchestrator import OperationsOrchestrator


def test_production_truthfulness_boundaries_preserved():
    orchestrator = OperationsOrchestrator()
    res = orchestrator.run_pipeline(
        app_data={"request_count": 1000, "failure_count": 0},
        is_production=False,
    )

    tm = res.certification.truthfulness_matrix
    assert tm["PRODUCTION_MONITORING_RUNTIME_VALIDATED"] == "NOT_EXECUTED"
    assert tm["PRODUCTION_ALERTING_RUNTIME_VALIDATED"] == "NOT_EXECUTED"
    assert tm["PRODUCTION_INCIDENT_RUNTIME_VALIDATED"] == "NOT_EXECUTED"
    assert tm["PRODUCTION_DEPLOYED"] == "NOT_EXECUTED"
    assert tm["LIVE_PRODUCTION_VALIDATED"] == "NOT_EXECUTED"
    assert tm["LIVE_PRODUCTION"] == "NOT_EXECUTED"


def test_production_flag_returns_not_executed():
    orchestrator = OperationsOrchestrator()
    res = orchestrator.run_pipeline(
        is_production=True,
    )

    assert res.certification.certification_status.value == "NOT_EXECUTED"
    assert res.certification.is_certified is False
