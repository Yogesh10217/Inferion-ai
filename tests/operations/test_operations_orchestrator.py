from app.operations.operations_orchestrator import OperationsOrchestrator


def test_operations_orchestrator_pipeline_success():
    orchestrator = OperationsOrchestrator()
    res = orchestrator.run_pipeline(
        app_data={"request_count": 1000, "failure_count": 0, "latency_p95": 100.0},
        health_data={"live": True, "ready": True, "health": True},
        evidence_level="CONTAINER_RUNTIME",
        is_production=False,
    )

    assert res.observation.status.value == "HEALTHY"
    assert res.error_budget.status.value == "HEALTHY"
    assert len(res.anomalies) == 0
    assert len(res.raw_alerts) == 0
    assert res.recovery_decision.recommendation.value == "NO_ACTION"
    assert res.recovery_decision.auto_execution_blocked is True
    assert res.deployment_health.is_healthy is True
    assert len(res.evidence.sha256_fingerprint) == 64
    assert res.certification.certification_status.value == "OPERATIONALLY_READY"
