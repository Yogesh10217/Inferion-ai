"""Unit tests for AgentDataFabricAdapter."""

import pytest
from app.data_fabric.data_source import DataSourceManager, DataSourceType
from app.data_fabric.agent_integration import AgentDataFabricAdapter
from app.data_fabric.governance import DataClassification


def test_agent_data_access_adapter():
    src_mgr = DataSourceManager()
    ds = src_mgr.create_source("Agent Source", DataSourceType.POSTGRES, "POSTGRES", tenant_id="tenant_agent")

    adapter = AgentDataFabricAdapter(source_manager=src_mgr)

    # Permitted access under same tenant
    decision = adapter.request_data_access(
        requester_id="agent_data_analyst",
        data_source_id=ds.id,
        tenant_id="tenant_agent",
        classification=DataClassification.INTERNAL,
    )
    assert decision.permitted is True

    # Blocked cross-tenant access
    decision_blocked = adapter.request_data_access(
        requester_id="agent_data_analyst",
        data_source_id=ds.id,
        tenant_id="tenant_other",
        classification=DataClassification.INTERNAL,
    )
    assert decision_blocked.permitted is False
    assert "Cross-tenant" in decision_blocked.reason
