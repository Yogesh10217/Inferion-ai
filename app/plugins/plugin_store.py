from abc import ABC, abstractmethod
from typing import List
from .plugin_manifest import PluginManifest

class PluginStore(ABC):
    @abstractmethod
    async def discover_plugins(self) -> List[str]:
        pass
        
    @abstractmethod
    async def load_manifest(self, plugin_id: str) -> PluginManifest:
        pass

class LocalFilesystemStore(PluginStore):
    def __init__(self, directory: str):
        self.directory = directory
        
    async def discover_plugins(self) -> List[str]:
        # Implementation would read subdirectories and find plugin.yaml/json
        return []

    async def load_manifest(self, plugin_id: str) -> PluginManifest:
        # Implementation would parse the manifest
        raise NotImplementedError
