"""
Tests for Multi-Tenant Scoping & Tenant Isolation Enforcement
"""

import pytest
from app.workflows.workflow_manager import WorkflowManager
from app.workflows.node import AgentNode
from app.workflows.exceptions import TenantIsolationError


def test_tenant_isolation_in_workflow_registry():
    mgr = WorkflowManager()
    wf_org1 = mgr.create_workflow("Org 1 Workflow", organization_id="org_1")
    wf_org2 = mgr.create_workflow("Org 2 Workflow", organization_id="org_2")

    org1_wfs = mgr.list_workflows(organization_id="org_1")
    org1_ids = [w.workflow_id for w in org1_wfs]

    assert wf_org1.workflow_id in org1_ids
    assert wf_org2.workflow_id not in org1_ids


@pytest.mark.asyncio
async def test_agent_node_requires_organization_id():
    agent_node = AgentNode("a1", "Agent", agent_id="agent_1")
    with pytest.raises(TenantIsolationError):
        await agent_node.execute({})
