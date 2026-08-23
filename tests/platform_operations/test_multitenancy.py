"""Unit tests for Multi-Tenancy & Tenant Isolation in Platform Operations."""

import pytest
from app.platform_operations.services import ServiceCatalogManager
from app.platform_operations.exceptions import ServiceNotFoundException


def test_cross_tenant_service_access_blocked():
    mgr = ServiceCatalogManager()
    s_a = mgr.register_service(tenant_id="tenant_A", name="Tenant A Service")

    # Tenant A access succeeds
    fetched = mgr.get_service(s_a.service_id, tenant_id="tenant_A")
    assert fetched.name == "Tenant A Service"

    # Tenant B access fails
    with pytest.raises(ServiceNotFoundException):
        mgr.get_service(s_a.service_id, tenant_id="tenant_B")
