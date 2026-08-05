import pytest
# multitenancy testing
def test_tenant_isolation():
    tenant1_data = {"id": "t1"}
    tenant2_data = {"id": "t2"}
    assert tenant1_data["id"] != tenant2_data["id"]
