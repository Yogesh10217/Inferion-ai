"""
Tests for Reliability Operations Orchestrator Module.
"""

from app.reliability.reliability_certification import ReliabilityCertificationDecision
from app.reliability.reliability_orchestrator import ReliabilityOperationsOrchestrator


def test_reliability_orchestrator_pipeline_execution():
    orchestrator = ReliabilityOperationsOrchestrator()
    res = orchestrator.execute_reliability_pipeline(real_production_configured=False)

    assert res.manager_validation_passed is True
    assert res.certification.certified is True
    assert res.certification.decision == ReliabilityCertificationDecision.RELIABILITY_CERTIFIED
    assert res.certification.live_production_recovery_validated is False
    assert res.dashboard_snapshot.overall_score > 90.0
    assert res.audit_result.valid is True
