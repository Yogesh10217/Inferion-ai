import pytest

from app.plugins.exceptions import PluginPermissionError
from app.plugins.plugin_context import PluginContext
from app.plugins.plugin_manifest import PluginPermission


def test_plugin_permissions():
    perms = [PluginPermission(action="events.publish", resource="*")]
    ctx = PluginContext("test_plugin", perms, None)

    # Should not raise
    assert ctx.check_permission("events.publish", "test.event") is True

    with pytest.raises(PluginPermissionError):
        ctx.check_permission("database.read", "users")
