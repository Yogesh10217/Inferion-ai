"""Unit tests for OrganizationManager."""

import pytest
from app.control_plane.organization import OrganizationManager
from app.control_plane.exceptions import OrganizationNotFoundException


def test_organization_crud_and_members():
    mgr = OrganizationManager()
    org = mgr.create_organization(name="Engineering Org", tenant_id="tenant_x")
    assert org.tenant_id == "tenant_x"

    # Add member
    mgr.add_member(org.organization_id, "user_1")
    assert "user_1" in org.members

    # Remove member
    mgr.remove_member(org.organization_id, "user_1")
    assert "user_1" not in org.members

    # Delete
    mgr.delete_organization(org.organization_id)
    with pytest.raises(OrganizationNotFoundException):
        mgr.get_organization(org.organization_id)
