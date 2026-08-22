"""Unit tests for HumanOversightEngine policy registration and evaluation."""

import pytest
from app.governance_platform.human_oversight import HumanOversightEngine, AutonomyLevel, OversightLevel


def test_human_oversight_policy_management():
    engine = HumanOversightEngine()
    pol = engine.create_policy("Financial Worker Oversight", "worker_fin_1", AutonomyLevel.CONSTRAINED_AUTONOMOUS, OversightLevel.APPROVAL_REQUIRED, tenant_id="t_ovs")

    assert pol.target_resource_id == "worker_fin_1"
    assert pol.autonomy_level == AutonomyLevel.CONSTRAINED_AUTONOMOUS
    assert pol.oversight_level == OversightLevel.APPROVAL_REQUIRED
