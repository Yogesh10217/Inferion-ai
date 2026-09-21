"""Unit tests for LifecycleManager."""

import pytest

from app.control_plane.exceptions import LifecycleException
from app.control_plane.lifecycle_manager import LifecycleManager, LifecycleState


def test_lifecycle_state_machine():
    lm = LifecycleManager()

    # Valid transition
    rec1 = lm.transition("agent_99", LifecycleState.PROVISIONING)
    assert rec1.current_state == LifecycleState.PROVISIONING

    rec2 = lm.transition("agent_99", LifecycleState.ACTIVE)
    assert rec2.current_state == LifecycleState.ACTIVE

    # Invalid transition ACTIVE -> PROVISIONING
    with pytest.raises(LifecycleException):
        lm.transition("agent_99", LifecycleState.PROVISIONING)
