from app.operations.operations_orchestrator import OperationsOrchestrator


def test_failure_simulation_degraded_runtime():
    orchestrator = OperationsOrchestrator()
    res = orchestrator.run_pipeline(
        app_data={"request_count": 1000, "failure_count": 150, "error_rate": 0.15, "latency_p95": 1200.0},
        health_data={"live": True, "ready": True, "health": True},
    )

    assert res.observation.status.value in ("DEGRADED", "UNHEALTHY")
    assert res.error_budget.status.value == "EXHAUSTED"
    assert len(res.anomalies) > 0
    assert len(res.raw_alerts) > 0
    assert res.recovery_decision.recommendation.value in ("ROLLBACK_RECOMMENDED", "EMERGENCY_INTERVENTION_REQUIRED")
    assert res.recovery_decision.auto_execution_blocked is True


def test_failure_simulation_dependency_failure():
    orchestrator = OperationsOrchestrator()
    res = orchestrator.run_pipeline(
        dependency_data={"postgresql": {"status": "UNHEALTHY", "latency_ms": 999.0}},
    )

    assert res.observation.status.value == "UNHEALTHY"
    assert any(a.anomaly_type.value == "DEPENDENCY_FAILURE" for a in res.anomalies)
