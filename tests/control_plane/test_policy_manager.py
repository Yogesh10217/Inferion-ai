"""Unit tests for PolicyManager."""

import pytest
from app.control_plane.policy_manager import PolicyManager, PolicyTargetType


def test_policy_creation_and_evaluation():
    pm = PolicyManager()
    pol = pm.create_policy(
        name="Restrict Executions",
        target_type=PolicyTargetType.TOOL,
        tenant_id="tenant_sec",
        rules={"deny_actions": ["delete_database"]},
    )
    assert pol.is_active is True

    eval_allowed = pm.evaluate_policy(PolicyTargetType.TOOL, "tool_1", "read_database", tenant_id="tenant_sec")
    assert eval_allowed["allowed"] is True

    eval_denied = pm.evaluate_policy(PolicyTargetType.TOOL, "tool_1", "delete_database", tenant_id="tenant_sec")
    assert eval_denied["allowed"] is False
    assert len(eval_denied["violations"]) == 1
