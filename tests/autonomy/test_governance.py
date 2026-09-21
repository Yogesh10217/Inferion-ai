"""
Tests for Execution Governance
"""

import pytest

from app.autonomy.exceptions import EmergencyStopException
from app.autonomy.execution_governance import ExecutionGovernanceEngine


def test_governance_emergency_stops():
    gov = ExecutionGovernanceEngine()
    gov.set_global_emergency_stop(True)

    with pytest.raises(EmergencyStopException) as exc:
        gov.validate_execution_start("tenant_1", "ws_1", cost_so_far=0.0)
    assert "GLOBAL EMERGENCY STOP" in str(exc.value)

    gov.set_global_emergency_stop(False)
    gov.set_tenant_emergency_stop("tenant_blocked", True)

    with pytest.raises(EmergencyStopException) as exc_t:
        gov.validate_execution_start("tenant_blocked", "ws_1", cost_so_far=0.0)
    assert "TENANT EMERGENCY STOP" in str(exc_t.value)
