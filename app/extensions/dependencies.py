"""Dependency Resolver with SemVer checking, cycle detection, and lockfiles."""

import logging
import re
from typing import Dict, Any, List, Set, Optional
from pydantic import BaseModel, Field

from app.extensions.extension import ExtensionManifest
from app.extensions.exceptions import ExtensionDependencyConflictException

logger = logging.getLogger(__name__)


class ExtensionLockfile(BaseModel):
    """Deterministic lockfile representing resolved dependency graph."""

    root_extension_id: str
    resolved_dependencies: Dict[str, str] = Field(default_factory=dict)  # pkg -> version
    lock_hash: str = ""


class DependencyResolver:
    """Resolves semantic version constraints, detects dependency cycles, and builds lockfiles."""

    @staticmethod
    def parse_semver(version_str: str) -> tuple:
        """Parse version string into tuple (major, minor, patch)."""
        clean = re.sub(r"[^\d.]", "", version_str)
        parts = [int(p) for p in clean.split(".") if p.isdigit()]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    def check_version_compatibility(self, version_str: str, constraint_str: str) -> bool:
        """Check if version satisfies constraint expression (e.g., '>=1.5.0')."""
        if not constraint_str or constraint_str == "*":
            return True

        v_tuple = self.parse_semver(version_str)

        if constraint_str.startswith(">="):
            c_tuple = self.parse_semver(constraint_str[2:])
            return v_tuple >= c_tuple
        elif constraint_str.startswith(">"):
            c_tuple = self.parse_semver(constraint_str[1:])
            return v_tuple > c_tuple
        elif constraint_str.startswith("<="):
            c_tuple = self.parse_semver(constraint_str[2:])
            return v_tuple <= c_tuple
        elif constraint_str.startswith("=="):
            c_tuple = self.parse_semver(constraint_str[2:])
            return v_tuple == c_tuple

        c_tuple = self.parse_semver(constraint_str)
        return v_tuple >= c_tuple

    def resolve_dependencies(
        self,
        manifest: ExtensionManifest,
        available_manifests: List[ExtensionManifest],
    ) -> ExtensionLockfile:
        """Resolve dependency graph and generate deterministic lockfile."""
        resolved: Dict[str, str] = {}
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        manifest_map = {m.identifier: m for m in available_manifests}

        def dfs(curr_manifest: ExtensionManifest) -> None:
            visited.add(curr_manifest.identifier)
            rec_stack.add(curr_manifest.identifier)

            for dep_pkg, constraint in curr_manifest.dependencies.items():
                if dep_pkg in rec_stack:
                    raise ExtensionDependencyConflictException(f"Circular dependency detected involving '{dep_pkg}'")

                target = manifest_map.get(dep_pkg)
                if not target:
                    raise ExtensionDependencyConflictException(f"Missing required dependency '{dep_pkg}'")

                if not self.check_version_compatibility(target.version, constraint):
                    raise ExtensionDependencyConflictException(
                        f"Incompatible dependency version for '{dep_pkg}': version {target.version} does not satisfy {constraint}"
                    )

                resolved[dep_pkg] = target.version

                if dep_pkg not in visited:
                    dfs(target)

            rec_stack.remove(curr_manifest.identifier)

        dfs(manifest)

        lock = ExtensionLockfile(
            root_extension_id=manifest.identifier,
            resolved_dependencies=resolved,
            lock_hash=f"hash_{len(resolved)}",
        )
        logger.info(f"[DEPENDENCY RESOLVER] Successfully resolved {len(resolved)} dependencies for '{manifest.identifier}'")
        return lock
