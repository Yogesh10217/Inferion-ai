"""Unit tests for Configuration rollback."""

from app.control_plane.configuration import ConfigurationManager, ConfigurationScope


def test_configuration_rollback():
    cfg_mgr = ConfigurationManager()

    # v1
    cfg_mgr.update_configuration(ConfigurationScope.TENANT, "t1", {"theme": "light", "rate": 100})
    # v2
    cfg_mgr.update_configuration(ConfigurationScope.TENANT, "t1", {"theme": "dark", "rate": 200})

    current = cfg_mgr.get_configuration(ConfigurationScope.TENANT, "t1")
    assert current["theme"] == "dark"

    # Rollback to v1
    rolled_back = cfg_mgr.rollback_configuration(ConfigurationScope.TENANT, "t1", target_version_number=1)
    assert rolled_back.settings["theme"] == "light"
    assert rolled_back.settings["rate"] == 100
