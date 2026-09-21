"""Unit tests for plugin manifest capability boundary enforcement."""

import pytest

from app.integrations.exceptions import PluginSecurityViolationException
from app.integrations.plugins import PluginManager, PluginManifest


def test_plugin_unauthorized_capability_boundary_violation():
    pm = PluginManager()
    manifest = PluginManifest(name="Restricted Plugin", capabilities=["READ_ONLY"])
    plug = pm.register_plugin(manifest, tenant_id="t_psec")

    # Attempting capability NOT declared in manifest must raise PluginSecurityViolationException
    with pytest.raises(PluginSecurityViolationException):
        pm.execute_plugin(plug.plugin_id, requested_capability="ADMIN_WRITE")
