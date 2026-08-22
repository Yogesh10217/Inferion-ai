"""Unit tests for PluginManager and plugin registration."""

import pytest
from app.integrations.plugins import PluginManager, PluginManifest


def test_plugin_registration_and_execution():
    pm = PluginManager()
    manifest = PluginManifest(name="Jira Helper", capabilities=["CREATE_TICKET", "SEARCH_ISSUES"])
    plug = pm.register_plugin(manifest, tenant_id="t_plug")

    res = pm.execute_plugin(plug.plugin_id, requested_capability="CREATE_TICKET")
    assert res["status"] == "SUCCESS"
