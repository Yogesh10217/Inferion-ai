import pytest
from app.plugins.plugin_loader import PluginLoader
from app.plugins.plugin_manifest import PluginManifest
from app.plugins.exceptions import PluginDependencyError


def test_dependency_validation_and_topological_sort():
    loader = PluginLoader()
    m1 = PluginManifest(
        id="base_plugin",
        name="Base",
        version="1.0.0",
        description="Base",
        author="Author",
        license="MIT",
        entrypoint="plugin.py:Plugin",
    )
    m2 = PluginManifest(
        id="dependent_plugin",
        name="Dependent",
        version="1.0.0",
        description="Dependent",
        author="Author",
        license="MIT",
        entrypoint="plugin.py:Plugin",
        dependencies={"base_plugin": ">=1.0.0"},
    )

    ordered = loader.validate_dependencies([m2, m1])
    assert len(ordered) == 2
    assert ordered[0].id == "base_plugin"
    assert ordered[1].id == "dependent_plugin"


def test_missing_dependency_raises_error():
    loader = PluginLoader()
    m = PluginManifest(
        id="orphan_plugin",
        name="Orphan",
        version="1.0.0",
        description="Orphan",
        author="Author",
        license="MIT",
        entrypoint="plugin.py:Plugin",
        dependencies={"non_existent": "1.0.0"},
    )
    with pytest.raises(PluginDependencyError):
        loader.validate_dependencies([m])
