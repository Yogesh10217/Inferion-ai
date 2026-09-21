"""Unit tests for ResourceGovernanceEngine."""

from app.governance.resource_governance import ResourceGovernanceEngine


def test_resource_governance_prepare_and_complete():
    gov = ResourceGovernanceEngine()
    gov.limits.max_memory_percent = 100.0

    res = gov.prepare_execution(component="agent", tenant_id="tenant_gov", estimated_tokens=50)
    assert res["status"] == "approved"
    assert res["active_concurrency"] == 1

    gov.complete_execution(component="agent", tenant_id="tenant_gov")
    assert gov._active_global_concurrency == 0
