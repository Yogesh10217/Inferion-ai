"""Unit tests for PolicySimulator."""

import pytest
from app.control_plane.policy_manager import PolicyManager, PolicyTargetType
from app.control_plane.policy_simulator import PolicySimulator
from app.control_plane.resource_registry import ResourceRegistry, ResourceType


def test_policy_dryrun_simulation():
    reg = ResourceRegistry()
    pm = PolicyManager()
    sim = PolicySimulator(policy_manager=pm, resource_registry=reg)

    reg.register_resource("tool_db", ResourceType.TOOL, "DB Tool", tenant_id="tenant_sim")

    report = sim.simulate_policy_impact(
        name="Block All Tools",
        target_type=PolicyTargetType.TOOL,
        rules={"deny_actions": ["*"]},
        tenant_id="tenant_sim",
    )
    assert report.total_resources_evaluated >= 1
    assert report.blocked_resources_count >= 1
