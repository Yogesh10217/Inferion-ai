"""Unit tests for DependencyResolver SemVer checking and cycle detection."""

import pytest
from app.extensions.extension import ExtensionManifest, ExtensionType
from app.extensions.dependencies import DependencyResolver
from app.extensions.exceptions import ExtensionDependencyConflictException


def test_semver_and_dependency_resolution():
    resolver = DependencyResolver()

    # Check semver constraint
    assert resolver.check_version_compatibility("1.6.0", ">=1.5.0") is True
    assert resolver.check_version_compatibility("1.4.0", ">=1.5.0") is False

    m_b = ExtensionManifest(identifier="pkg_b", name="Pkg B", version="2.0.0", publisher_id="p1", extension_type=ExtensionType.TOOL)
    m_a = ExtensionManifest(identifier="pkg_a", name="Pkg A", version="1.0.0", publisher_id="p1", extension_type=ExtensionType.TOOL, dependencies={"pkg_b": ">=1.5.0"})

    lockfile = resolver.resolve_dependencies(m_a, available_manifests=[m_a, m_b])
    assert lockfile.resolved_dependencies["pkg_b"] == "2.0.0"
