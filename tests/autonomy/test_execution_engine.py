"""
Tests for Autonomous Execution Engine
"""

import pytest
from app.autonomy.execution_engine import AutonomousExecutionEngine


@pytest.mark.asyncio
async def test_execute_goal_end_to_end():
    engine = AutonomousExecutionEngine()
    res = await engine.execute_goal("Autonomous data backup", tenant_id="tenant_1")

    assert res["status"] == "COMPLETED"
    assert res["execution_id"].startswith("auto_exec_")
    assert res["cost"] == 0.01

    # Check recovery
    recovered = engine.recover_execution(res["execution_id"], tenant_id="tenant_1")
    assert recovered["status"] == "RECOVERED"
    assert recovered["step_number"] == 2
