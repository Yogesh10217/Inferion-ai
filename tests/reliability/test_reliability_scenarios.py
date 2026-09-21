"""
Tests for Reliability Scenarios Engine.
"""

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel
from app.reliability.reliability_scenarios import ReliabilityScenarioEngine


def test_evaluate_all_canonical_scenarios():
    engine = ReliabilityScenarioEngine()
    results = engine.evaluate_all_scenarios(mode=ReliabilityEvidenceLevel.SIMULATION_RUNTIME)
    assert len(results) == 14
    for res in results:
        assert res.handled is True
        assert res.status == "PASSED"
        assert res.evidence_level == ReliabilityEvidenceLevel.SIMULATION_RUNTIME
