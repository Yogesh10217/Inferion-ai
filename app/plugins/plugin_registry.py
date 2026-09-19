import json
import os
import threading
import time
from typing import Any, Dict, List, Optional

from .plugin import Plugin


class PluginRecord:
    def __init__(
        self,
        plugin_id: str,
        version: str,
        enabled: bool = False,
        dependencies: Optional[Dict[str, str]] = None,
        installed_at: Optional[float] = None,
        health_status: str = "healthy",
    ):
        self.plugin_id = plugin_id
        self.version = version
        self.enabled = enabled
        self.dependencies = dependencies or {}
        self.installed_at = installed_at or time.time()
        self.health_status = health_status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "version": self.version,
            "enabled": self.enabled,
            "dependencies": self.dependencies,
            "installed_at": self.installed_at,
            "health_status": self.health_status,
        }


class PluginRegistry:
    """Thread-safe persistent registry tracking installed, enabled, and disabled plugins."""

    def __init__(self, persistence_file: Optional[str] = None):
        self._lock = threading.RLock()
        self._persistence_file = persistence_file or "plugins_registry.json"
        self._plugins: Dict[str, Plugin] = {}
        self._records: Dict[str, PluginRecord] = {}
        self._load_persistence()

    def _load_persistence(self):
        with self._lock:
            if os.path.exists(self._persistence_file):
                try:
                    with open(self._persistence_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for pid, rec_data in data.items():
                        self._records[pid] = PluginRecord(
                            plugin_id=rec_data["plugin_id"],
                            version=rec_data["version"],
                            enabled=rec_data.get("enabled", False),
                            dependencies=rec_data.get("dependencies", {}),
                            installed_at=rec_data.get("installed_at"),
                            health_status=rec_data.get("health_status", "healthy"),
                        )
                except Exception:
                    pass

    def _save_persistence(self):
        with self._lock:
            if self._persistence_file:
                try:
                    data = {pid: rec.to_dict() for pid, rec in self._records.items()}
                    with open(self._persistence_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                except Exception:
                    pass

    def register(self, plugin: Plugin, enabled: Optional[bool] = None):
        with self._lock:
            pid = plugin.manifest.id
            self._plugins[pid] = plugin

            existing_record = self._records.get(pid)
            is_enabled = enabled if enabled is not None else (existing_record.enabled if existing_record else False)
            plugin.is_enabled = is_enabled

            self._records[pid] = PluginRecord(
                plugin_id=pid,
                version=plugin.manifest.version,
                enabled=is_enabled,
                dependencies=plugin.manifest.dependencies,
                health_status="healthy",
            )
            self._save_persistence()

    def unregister(self, plugin_id: str):
        with self._lock:
            self._plugins.pop(plugin_id, None)
            self._records.pop(plugin_id, None)
            self._save_persistence()

    def get(self, plugin_id: str) -> Optional[Plugin]:
        with self._lock:
            return self._plugins.get(plugin_id)

    def get_record(self, plugin_id: str) -> Optional[PluginRecord]:
        with self._lock:
            return self._records.get(plugin_id)

    def set_enabled(self, plugin_id: str, enabled: bool):
        with self._lock:
            plugin = self._plugins.get(plugin_id)
            if plugin:
                plugin.is_enabled = enabled
            record = self._records.get(plugin_id)
            if record:
                record.enabled = enabled
                self._save_persistence()

    def set_health(self, plugin_id: str, status: str):
        with self._lock:
            record = self._records.get(plugin_id)
            if record:
                record.health_status = status
                self._save_persistence()

    def get_all(self) -> List[Plugin]:
        with self._lock:
            return list(self._plugins.values())

    def get_enabled(self) -> List[Plugin]:
        with self._lock:
            return [p for p in self._plugins.values() if p.is_enabled]

    def get_disabled(self) -> List[Plugin]:
        with self._lock:
            return [p for p in self._plugins.values() if not p.is_enabled]
