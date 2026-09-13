"""
Tests for Reliability Dashboard Snapshot.
"""

from app.reliability.reliability_dashboard import ReliabilityDashboardSnapshot
from app.reliability.reliability_engine import ReliabilityStatus
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


def test_dashboard_snapshot_generation():
    snapshot = ReliabilityDashboardSnapshot(
        overall_status=ReliabilityStatus.HEALTHY,
        reliability_score=98.5,
        resilience_score=98.5,
        slo_status="COMPLIANT",
        error_budget_remaining_percentage=99.5,
        active_incidents_count=0,
        active_alerts_count=0,
        open_security_risks_count=0,
        dependency_health_status="HEALTHY",
        recovery_status="RECOVERY_READY",
        chaos_experiment_status="IDLE",
        disaster_recovery_readiness_status="READY",
        certification_decision="RELIABILITY_CERTIFIED",
        auto_execution_blocked=True,
        evidence_level=ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    )
    d = snapshot.to_dict()
    assert d["overall_status"] == "HEALTHY"
    assert d["reliability_score"] == 98.5
    assert d["auto_execution_blocked"] is True
