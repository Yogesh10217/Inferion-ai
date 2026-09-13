"""
Tests for Disaster Recovery Simulation Engine Module.
"""

from app.reliability.disaster_recovery_simulation import DisasterRecoverySimulationEngine


def test_dr_simulation_rto_rpo_targets():
    engine = DisasterRecoverySimulationEngine()
    res = engine.run_dr_simulation(observed_rto_minutes=10.0, observed_rpo_minutes=2.0)
    assert res.simulation_validated is True
    assert res.rto_simulation_status == "RTO_SIMULATION_VALIDATED"
    assert res.rpo_simulation_status == "RPO_SIMULATION_VALIDATED"
    assert res.production_execution is False
    assert res.production_rto_validated is False
    assert res.production_rpo_validated is False
