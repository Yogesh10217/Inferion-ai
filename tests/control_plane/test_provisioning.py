"""Unit tests for ProvisioningEngine."""

from app.control_plane.provisioning import ProvisioningEngine


def test_automated_tenant_provisioning():
    pe = ProvisioningEngine()
    bundle = pe.provision_new_tenant(tenant_name="Stark Industries", org_name="R&D")

    assert bundle.status == "PROVISIONED"
    assert bundle.tenant["name"] == "Stark Industries"
    assert bundle.organization["name"] == "R&D"
    assert bundle.workspace["name"] == "Default Workspace"
