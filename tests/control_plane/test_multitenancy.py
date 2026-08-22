"""Unit & Security tests for Tenant Isolation in Control Plane."""

import pytest
from app.control_plane.manager import ControlPlaneManager
from app.security.exceptions import TenantAccessDeniedError


def test_strict_tenant_isolation():
    cp = ControlPlaneManager()

    # Create two isolated tenants
    t1 = cp.tenant_manager.create_tenant("Tenant Alpha")
    t2 = cp.tenant_manager.create_tenant("Tenant Beta")

    # Create organization in Tenant Alpha
    org_a = cp.organization_manager.create_organization("Org Alpha", tenant_id=t1.tenant_id)

    # Listing organizations for Tenant Beta must not contain Org Alpha
    beta_orgs = cp.organization_manager.list_organizations(tenant_id=t2.tenant_id)
    assert not any(o.organization_id == org_a.organization_id for o in beta_orgs)
