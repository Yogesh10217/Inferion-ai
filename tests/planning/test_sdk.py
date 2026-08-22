"""
Tests for Planning SDK Clients
"""

import pytest
from sdk.python.llm_engine.planning import PlanningClient


def test_python_sdk_planning_client():
    client = PlanningClient(base_url="http://localhost:8000")
    assert hasattr(client, "create")
    assert hasattr(client, "list")
    assert hasattr(client, "get")
    assert hasattr(client, "update")
    assert hasattr(client, "delete")
    assert hasattr(client, "simulate")
    assert hasattr(client, "execute")
    assert hasattr(client, "reflect")
    assert hasattr(client, "optimize")
    assert hasattr(client, "metrics")
    assert hasattr(client, "billing")
    assert hasattr(client, "history")
