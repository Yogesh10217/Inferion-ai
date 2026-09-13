"""
Tests for Reliability Dashboard Snapshot.
"""

from app.reliability.reliability_dashboard import ReliabilityDashboardSnapshot
from app.reliability.reliability_engine import ReliabilityStatus
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


def test_dashboard_snapshot_generation():
    snapshot = ReliabilityDashboardSnapshot(
        overall_status=ReliabilityStatus.RELIABLE,
        overall_score=98.5,
        availability_percentage=99.95,
        active_incidents_count=0,
        active_alerts_count=0,
        slo_status="COMPLIANT",
        error_budget_remaining_percentage=99.5,
        recovery_readiness_status="RECOVERY_READY",
        backup_readiness_status="READY",
        failover_readiness_status="READY",
        business_continuity_status="CONTINUITY_READY",
        latest_recovery_action="MONITOR",
        auto_execution_blocked=True,
        evidence_level=ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    )
    d = snapshot.to_dict()
    assert d["overall_status"] == "RELIABLE"
    assert d["overall_score"] == 98.5
    assert d["auto_execution_blocked"] is True
