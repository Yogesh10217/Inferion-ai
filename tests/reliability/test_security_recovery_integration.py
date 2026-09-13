"""
Tests for Security Recovery Integration Module.
"""

from app.reliability.recovery_state_machine import RecoveryState, RecoveryStateMachine
from app.reliability.security_recovery_integration import SecurityRecoveryIntegration


def test_security_incident_recovery_integration():
    integration = SecurityRecoveryIntegration()
    sm = RecoveryStateMachine()

    res = integration.process_security_event(threat_level="CRITICAL", threat_type="DATA_TAMPERING", state_machine=sm)
    assert res.threat_detected is True
    assert res.auto_execution_blocked is True
    assert sm.current_state in (RecoveryState.INCIDENT_DETECTED, RecoveryState.RECOVERY_ANALYSIS)
