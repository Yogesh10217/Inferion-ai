"""Unit tests for ConfigurationManager."""

from app.control_plane.configuration import ConfigurationManager, ConfigurationScope


def test_configuration_inheritance_and_versioning():
    cfg_mgr = ConfigurationManager()

    # Scope 1: Platform default
    ver1 = cfg_mgr.update_configuration(
        scope=ConfigurationScope.PLATFORM,
        target_id="global",
        settings_update={"max_tokens": 1000, "timeout": 30},
    )
    assert ver1.version_number == 1

    # Scope 2: Workspace override
    cfg_mgr.update_configuration(
        scope=ConfigurationScope.WORKSPACE,
        target_id="ws_1",
        settings_update={"timeout": 60},
    )

    platform_cfg = cfg_mgr.get_configuration(ConfigurationScope.PLATFORM, "global")
    ws_cfg = cfg_mgr.get_configuration(ConfigurationScope.WORKSPACE, "ws_1", parent_configs=[platform_cfg])

    assert ws_cfg["max_tokens"] == 1000
    assert ws_cfg["timeout"] == 60  # Override applied
