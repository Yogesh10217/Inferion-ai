"""Unit tests for Bounded Autonomous Operations Engine."""

import pytest

from app.governance_platform.risk import RiskLevel
from app.platform_operations.autonomous_operations import (
    AutonomousOperationsEngine,
    AutonomyLevel,
)
from app.platform_operations.exceptions import AutonomousActionDeniedException
from app.platform_operations.remediation import RemediationPlanner, RemediationStep, RemediationStrategy


def test_autonomous_operation_execution():
    planner = RemediationPlanner()
    auto_engine = AutonomousOperationsEngine(remediation_planner=planner)

    step = RemediationStep(
        strategy=RemediationStrategy.RETRY,
        target_resource_id="svc_1",
        action_description="Retry transient connection",
        expected_effect="Recover",
        risk_level=RiskLevel.LOW,
    )
    plan = planner.create_remediation_plan("t1", "inc_1", "svc_1", [step])

    op = auto_engine.execute_autonomous_remediation(
        "t1", plan.plan_id, autonomy_level=AutonomyLevel.CONSTRAINED_AUTONOMOUS
    )
    assert op.status == "SUCCESSFUL"


def test_high_risk_autonomous_operation_denied():
    planner = RemediationPlanner()
    auto_engine = AutonomousOperationsEngine(remediation_planner=planner)

    step = RemediationStep(
        strategy=RemediationStrategy.ROLLBACK,
        target_resource_id="svc_1",
        action_description="Production Rollback",
        expected_effect="Recover",
        risk_level=RiskLevel.CRITICAL,
    )
    plan = planner.create_remediation_plan("t1", "inc_1", "svc_1", [step])

    with pytest.raises(AutonomousActionDeniedException):
        auto_engine.execute_autonomous_remediation("t1", plan.plan_id)
