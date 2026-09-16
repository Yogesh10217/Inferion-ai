import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from .exceptions import PluginLoadError
from .plugin_manifest import PluginManifest

logger = logging.getLogger(__name__)


class PluginStore(ABC):
    @abstractmethod
    async def discover_plugins(self) -> List[str]:
        pass

    @abstractmethod
    async def load_manifest(self, plugin_id: str) -> PluginManifest:
        pass


class LocalFilesystemStore(PluginStore):
    def __init__(self, directory: str):
        self.directory = os.path.abspath(directory)
        self._manifest_cache: Dict[str, Tuple[str, PluginManifest]] = {}  # plugin_id -> (dir_path, manifest)

    async def discover_plugins(self) -> List[str]:
        """Scan configured directory for subdirectories containing manifest files."""
        if not os.path.exists(self.directory):
            logger.warning(f"Plugin directory does not exist: {self.directory}")
            return []

        discovered: List[str] = []
        for entry in os.listdir(self.directory):
            full_path = os.path.join(self.directory, entry)
            if os.path.isdir(full_path):
                manifest_file = None
                for fname in ["manifest.json", "plugin.json"]:
                    candidate = os.path.join(full_path, fname)
                    if os.path.exists(candidate):
                        manifest_file = candidate
                        break

                if manifest_file:
                    try:
                        manifest = PluginManifest.parse_manifest_file(manifest_file)
                        self._manifest_cache[manifest.id] = (full_path, manifest)
                        discovered.append(manifest.id)
                    except Exception as e:
                        logger.error(f"Failed to parse manifest at {manifest_file}: {e}")
        return discovered

    async def load_manifest(self, plugin_id: str) -> PluginManifest:
        if plugin_id in self._manifest_cache:
            return self._manifest_cache[plugin_id][1]

        # Fallback manual discovery if cache miss
        await self.discover_plugins()
        if plugin_id in self._manifest_cache:
            return self._manifest_cache[plugin_id][1]

        raise PluginLoadError(f"Plugin '{plugin_id}' not found in filesystem store: {self.directory}")

    def get_plugin_dir(self, plugin_id: str) -> Optional[str]:
        if plugin_id in self._manifest_cache:
            return self._manifest_cache[plugin_id][0]
        return None
