"""
Tests for Autonomy & Workers SDK Clients
"""

import pytest
from sdk.python.llm_engine.autonomy import AutonomyClient, WorkersClient


def test_python_sdk_autonomy_and_workers_clients():
    ac = AutonomyClient(base_url="http://localhost:8000")
    wc = WorkersClient(base_url="http://localhost:8000")

    assert hasattr(ac, "submit_goal")
    assert hasattr(ac, "pause")
    assert hasattr(ac, "resume")
    assert hasattr(ac, "stop")

    assert hasattr(wc, "create")
    assert hasattr(wc, "list")
    assert hasattr(wc, "get")
    assert hasattr(wc, "terminate")
    assert hasattr(wc, "assign_goal")
