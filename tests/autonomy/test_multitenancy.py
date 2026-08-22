"""
Tests for Multi-Tenant Isolation in Autonomy Engine
"""

import pytest
from app.autonomy.execution_governance import ExecutionGovernanceEngine
from app.autonomy.exceptions import EmergencyStopException


def test_tenant_emergency_stop_isolation():
    gov = ExecutionGovernanceEngine()
    gov.set_tenant_emergency_stop("tenant_blocked", True)

    # Allowed tenant executes without error
    gov.validate_execution_start("tenant_allowed", "ws_1", cost_so_far=0.0)

    # Blocked tenant raises EmergencyStopException
    with pytest.raises(EmergencyStopException):
        gov.validate_execution_start("tenant_blocked", "ws_1", cost_so_far=0.0)
