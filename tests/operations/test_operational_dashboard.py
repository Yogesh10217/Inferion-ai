from app.operations.operational_dashboard import OperationalDashboardSnapshot


def test_operational_dashboard_snapshot():
    snap = OperationalDashboardSnapshot(
        timestamp="2026-09-13T09:00:00Z",
        platform_status="HEALTHY",
        availability=1.0,
        error_rate=0.0,
        latency_p50=45.0,
        latency_p95=120.0,
        latency_p99=250.0,
        slo_status_counts={"MET": 5},
        error_budget_status="HEALTHY",
        active_alerts_count=0,
        active_incidents_count=0,
        deployment_health_score=100.0,
        dependency_status={"postgresql": "HEALTHY"},
        certification_status="OPERATIONALLY_READY",
        evidence_level="CONTAINER_RUNTIME",
    )
    d = snap.to_dict()
    assert d["platform_status"] == "HEALTHY"
    assert d["certification_status"] == "OPERATIONALLY_READY"
