"""Unit tests for TenantManager & Tenant Lifecycle."""

import pytest
from app.control_plane.tenant import TenantManager, TenantStatus
from app.control_plane.exceptions import TenantNotFoundException, LifecycleException


def test_tenant_lifecycle_flow():
    mgr = TenantManager()
    t = mgr.create_tenant(name="Acme Corp")
    assert t.status == TenantStatus.ACTIVE
    assert t.slug == "acme-corp"

    # Suspend
    suspended = mgr.suspend_tenant(t.tenant_id, reason="Maintenance")
    assert suspended.status == TenantStatus.SUSPENDED

    # Activate
    activated = mgr.activate_tenant(t.tenant_id)
    assert activated.status == TenantStatus.ACTIVE

    # Soft Delete
    deleted = mgr.delete_tenant(t.tenant_id)
    assert deleted.status == TenantStatus.DELETED

    # Action on deleted tenant raises error
    with pytest.raises(LifecycleException):
        mgr.activate_tenant(t.tenant_id)
