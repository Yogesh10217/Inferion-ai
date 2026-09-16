import importlib
import importlib.util
import logging
import os
import sys
from typing import Any, Dict, List, Set, Type

from .exceptions import PluginDependencyError, PluginLoadError
from .plugin import Plugin
from .plugin_manifest import PluginManifest

logger = logging.getLogger(__name__)


class PluginLoader:
    """Handles dynamic loading, manifest parsing, dependency graphs, and module isolation."""

    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}

    def load_plugin_class_from_file(self, file_path: str, class_name: str, plugin_id: str) -> Type[Plugin]:
        """Dynamically load Python module from file path and extract Plugin subclass."""
        if not os.path.exists(file_path):
            raise PluginLoadError(f"Plugin file not found: {file_path}")

        module_name = f"app.plugins.dynamic.{plugin_id}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Cannot load module spec for {file_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            self._loaded_modules[plugin_id] = module

            plugin_class = getattr(module, class_name, None)
            if plugin_class is None:
                raise PluginLoadError(f"Class '{class_name}' not found in {file_path}")
            if not issubclass(plugin_class, Plugin):
                raise PluginLoadError(f"Class '{class_name}' is not a subclass of Plugin")

            return plugin_class
        except Exception as e:
            logger.error(f"Failed to load plugin class '{class_name}' from {file_path}: {e}")
            raise PluginLoadError(f"Failed to load plugin '{plugin_id}': {e}") from e

    def validate_dependencies(self, manifests: List[PluginManifest]) -> List[PluginManifest]:
        """Resolve dependency graph, detect circular dependencies, and return topological sort order."""
        manifest_map: Dict[str, PluginManifest] = {m.id: m for m in manifests}
        graph: Dict[str, List[str]] = {m.id: list(m.dependencies.keys()) for m in manifests}

        # Validate missing dependencies
        for m in manifests:
            for dep_id, ver_req in m.dependencies.items():
                if dep_id not in manifest_map:
                    raise PluginDependencyError(
                        f"Plugin '{m.id}' missing required dependency '{dep_id}' (version {ver_req})"
                    )

        # Detect circular dependencies using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        order: List[str] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    raise PluginDependencyError(
                        f"Circular dependency detected involving plugin '{node}' and '{neighbor}'"
                    )
            rec_stack.remove(node)
            order.append(node)

        for plugin_id in manifest_map:
            if plugin_id not in visited:
                dfs(plugin_id)

        # Return ordered manifests
        return [manifest_map[pid] for pid in order if pid in manifest_map]
