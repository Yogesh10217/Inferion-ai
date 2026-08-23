"""Unit tests for Multi-Tenancy & Zero Leakage Isolation."""

import pytest
from app.application_platform.application import ApplicationRegistry
from app.application_platform.exceptions import ApplicationNotFoundException


def test_tenant_isolation_access_denied():
    registry = ApplicationRegistry()
    
    app_a = registry.create_application(tenant_id="tenant_A", name="Tenant A App")
    
    # Tenant B attempt to access Tenant A application MUST fail
    with pytest.raises(ApplicationNotFoundException):
        registry.get_application(app_a.application_id, tenant_id="tenant_B")

    # Tenant B list MUST NOT reveal Tenant A applications
    apps_b = registry.list_applications("tenant_B")
    assert len(apps_b) == 0
