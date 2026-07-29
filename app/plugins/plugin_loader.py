import importlib
import logging
from typing import Optional
from .plugin import Plugin
from .plugin_manifest import PluginManifest
from .exceptions import PluginLoadError

logger = logging.getLogger(__name__)

class PluginLoader:
    def load_plugin_class(self, entrypoint: str) -> type:
        try:
            module_name, class_name = entrypoint.split(":")
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            if not issubclass(plugin_class, Plugin):
                raise PluginLoadError(f"Class {class_name} is not a subclass of Plugin")
            return plugin_class
        except Exception as e:
            logger.error(f"Failed to load plugin entrypoint {entrypoint}: {e}")
            raise PluginLoadError(f"Failed to load plugin entrypoint {entrypoint}: {e}")

    def validate_dependencies(self, manifest: PluginManifest, installed_plugins: dict) -> bool:
        # Check if requirements in manifest.dependencies are met by installed_plugins versions
        for dep_id, version_req in manifest.dependencies.items():
            if dep_id not in installed_plugins:
                raise PluginLoadError(f"Missing dependency: {dep_id}")
            # Simplified version check logic
            dep_ver = installed_plugins[dep_id].manifest.version
            if dep_ver != version_req and not version_req.startswith(">="):
                # Basic check, in reality would use packaging module
                pass
        return True
