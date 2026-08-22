"""Unit tests for Control Plane Database Models."""

import pytest
from app.control_plane.models import TenantModel, OrganizationModel, WorkspaceModel


def test_control_plane_models_instantiation():
    t_model = TenantModel(name="Model Tenant", slug="model-tenant", status="ACTIVE")
    assert t_model.name == "Model Tenant"
    assert t_model.status == "ACTIVE"

    o_model = OrganizationModel(tenant_id="t1", name="Model Org", slug="model-org")
    assert o_model.tenant_id == "t1"

    w_model = WorkspaceModel(organization_id="o1", tenant_id="t1", name="Model WS", environment="DEVELOPMENT")
    assert w_model.environment == "DEVELOPMENT"

