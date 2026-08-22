"""Unit tests for ResourceRegistry."""

import pytest
from app.control_plane.resource_registry import ResourceRegistry, ResourceType
from app.control_plane.exceptions import ResourceNotFoundException


def test_resource_registration_and_search():
    reg = ResourceRegistry()
    res = reg.register_resource(
        resource_id="agent_alpha",
        resource_type=ResourceType.AGENT,
        name="Alpha Support Agent",
        tenant_id="t_1",
    )
    assert res.resource_type == ResourceType.AGENT

    fetched = reg.get_resource("agent_alpha")
    assert fetched.name == "Alpha Support Agent"

    results = reg.search_resources("alpha")
    assert len(results) == 1

    reg.unregister_resource("agent_alpha")
    with pytest.raises(ResourceNotFoundException):
        reg.get_resource("agent_alpha")
