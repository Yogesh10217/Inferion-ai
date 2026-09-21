"""
Tests for SDK Team Clients
"""

from sdk.python.llm_engine.teams import TeamsClient


def test_python_sdk_teams_client():
    client = TeamsClient(base_url="http://localhost:8000")
    assert hasattr(client, "create")
    assert hasattr(client, "list")
    assert hasattr(client, "get")
    assert hasattr(client, "update")
    assert hasattr(client, "delete")
    assert hasattr(client, "run")
    assert hasattr(client, "pause")
    assert hasattr(client, "resume")
    assert hasattr(client, "cancel")
    assert hasattr(client, "members")
    assert hasattr(client, "messages")
    assert hasattr(client, "history")
    assert hasattr(client, "metrics")
    assert hasattr(client, "billing")
