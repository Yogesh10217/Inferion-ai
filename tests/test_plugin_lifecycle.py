import pytest

from app.plugins.exceptions import PluginLifecycleError
from app.plugins.plugin_lifecycle import PluginLifecycleManager, PluginState


def test_lifecycle_state_machine():
    manager = PluginLifecycleManager()
    pid = "plugin_state_test"

    assert manager.get_state(pid) == PluginState.UNLOADED

    # Valid transitions
    manager.transition_to(pid, PluginState.DISCOVERED)
    assert manager.get_state(pid) == PluginState.DISCOVERED

    manager.transition_to(pid, PluginState.LOADED)
    assert manager.get_state(pid) == PluginState.LOADED

    manager.transition_to(pid, PluginState.INITIALIZED)
    assert manager.get_state(pid) == PluginState.INITIALIZED

    manager.transition_to(pid, PluginState.ENABLED)
    assert manager.get_state(pid) == PluginState.ENABLED

    # Invalid transition (ENABLED -> DISCOVERED directly)
    with pytest.raises(PluginLifecycleError):
        manager.transition_to(pid, PluginState.DISCOVERED)
