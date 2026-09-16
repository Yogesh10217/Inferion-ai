import logging
import os
from typing import Any, Dict, List, Optional

from .exceptions import PluginLifecycleError, PluginLoadError
from .plugin import Plugin
from .plugin_context import PluginContext
from .plugin_execution import (
    PLUGIN_DISABLED_TOTAL,
    PLUGIN_ENABLED_TOTAL,
    PLUGIN_LOAD_TOTAL,
    PluginExecutor,
)
from .plugin_hooks import PluginHook
from .plugin_lifecycle import PluginLifecycleManager
from .plugin_loader import PluginLoader
from .plugin_manifest import PluginManifest
from .plugin_registry import PluginRegistry
from .plugin_store import LocalFilesystemStore

logger = logging.getLogger(__name__)


class PluginManager:
    """Central orchestrator managing full plugin lifecycles, discovery, hooks, and execution."""

    def __init__(self, plugin_dir: Optional[str] = None, event_bus: Optional[Any] = None):
        base_dir = plugin_dir or os.path.join(os.path.dirname(__file__), "examples")
        self.store = LocalFilesystemStore(base_dir)
        self.registry = PluginRegistry()
        self.lifecycle = PluginLifecycleManager()
        self.loader = PluginLoader()
        self.executor = PluginExecutor()
        self.event_bus = event_bus

    async def initialize(self) -> None:
        """Startup loading: discover, load, initialize, and enable registered plugins."""
        logger.info("Initializing PluginManager...")
        await self.load_plugins()

    async def load_plugins(self) -> List[str]:
        """Discover and load all valid plugins from store."""
        discovered_ids = await self.store.discover_plugins()
        manifests: List[PluginManifest] = []
        for pid in discovered_ids:
            try:
                m = await self.store.load_manifest(pid)
                manifests.append(m)
            except Exception as e:
                logger.error(f"Failed loading manifest for '{pid}': {e}")

        # Resolve dependencies and sort load order
        try:
            ordered_manifests = self.loader.validate_dependencies(manifests)
        except Exception as e:
            logger.error(f"Dependency validation failed: {e}")
            ordered_manifests = manifests

        loaded_ids: List[str] = []
        for manifest in ordered_manifests:
            try:
                await self.load_plugin(manifest.id)
                loaded_ids.append(manifest.id)
            except Exception as e:
                logger.error(f"Failed to load plugin '{manifest.id}': {e}")

        self._update_metrics()
        return loaded_ids

    async def load_plugin(self, plugin_id: str) -> Plugin:
        """Load a single plugin into registry."""
        manifest = await self.store.load_manifest(plugin_id)
        plugin_dir = self.store.get_plugin_dir(plugin_id)
        if not plugin_dir:
            raise PluginLoadError(f"Plugin directory for '{plugin_id}' not found")

        # Parse entrypoint string "file.py:ClassName"
        entry = manifest.entrypoint
        if ":" in entry:
            file_rel, class_name = entry.split(":")
        else:
            file_rel, class_name = "plugin.py", entry

        file_path = os.path.join(plugin_dir, file_rel)
        plugin_class = self.loader.load_plugin_class_from_file(file_path, class_name, plugin_id)

        context = PluginContext(
            plugin_id=plugin_id,
            permissions=manifest.permissions,
            event_bus=self.event_bus,
        )

        plugin = plugin_class(manifest, context)
        await self.lifecycle.initialize(plugin)
        self.registry.register(plugin)

        # Enable if persistence record specifies enabled
        rec = self.registry.get_record(plugin_id)
        if rec and rec.enabled:
            await self.lifecycle.enable(plugin)

        PLUGIN_LOAD_TOTAL.labels(plugin_id=plugin_id).inc()
        await self.dispatch_hook(PluginHook.PLUGIN_LOADED, plugin_id=plugin_id)
        return plugin

    async def enable_plugin(self, plugin_id: str) -> None:
        """Enable a registered plugin."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            raise PluginLifecycleError(f"Plugin '{plugin_id}' not found")
        await self.lifecycle.enable(plugin)
        self.registry.set_enabled(plugin_id, True)
        self._update_metrics()

    async def disable_plugin(self, plugin_id: str) -> None:
        """Disable an enabled plugin."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            raise PluginLifecycleError(f"Plugin '{plugin_id}' not found")
        await self.lifecycle.disable(plugin)
        self.registry.set_enabled(plugin_id, False)
        self._update_metrics()

    async def reload_plugin(self, plugin_id: str) -> Plugin:
        """Unload and reload a plugin."""
        await self.unload_plugin(plugin_id)
        return await self.load_plugin(plugin_id)

    async def unload_plugin(self, plugin_id: str) -> None:
        """Unload a plugin from memory."""
        plugin = self.registry.get(plugin_id)
        if plugin:
            if plugin.is_enabled:
                await self.disable_plugin(plugin_id)
            await self.lifecycle.uninstall(plugin)
            self.registry.unregister(plugin_id)
            await self.dispatch_hook(PluginHook.PLUGIN_UNLOADED, plugin_id=plugin_id)
            self._update_metrics()

    async def install_plugin(self, plugin_id: str) -> Plugin:
        """Install and load a discovered plugin."""
        plugin = await self.load_plugin(plugin_id)
        await self.lifecycle.install(plugin)
        return plugin

    async def uninstall_plugin(self, plugin_id: str) -> None:
        """Uninstall and remove plugin."""
        await self.unload_plugin(plugin_id)

    async def dispatch_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute a hook across all enabled plugins matching hook handlers."""
        results = []
        enabled_plugins = self.registry.get_enabled()

        # Format method name: "before_request" -> "on_before_request" or "on_before_request"
        clean_name = hook_name.value if isinstance(hook_name, PluginHook) else str(hook_name)
        method_name = f"on_{clean_name.replace('.', '_')}"

        for plugin in enabled_plugins:
            handler = getattr(plugin, method_name, None)
            if callable(handler):
                try:
                    res = await self.executor.execute(
                        plugin.manifest.id,
                        handler,
                        *args,
                        hook_name=clean_name,
                        **kwargs,
                    )
                    results.append(res)
                except Exception as e:
                    logger.error(f"Plugin '{plugin.manifest.id}' hook '{clean_name}' failed: {e}")
                    self.registry.set_health(plugin.manifest.id, "degraded")
        return results

    def get_plugin_health(self, plugin_id: str) -> Dict[str, Any]:
        """Get plugin status and health diagnostics."""
        plugin = self.registry.get(plugin_id)
        record = self.registry.get_record(plugin_id)
        if not plugin or not record:
            return {"plugin_id": plugin_id, "status": "not_found", "health": "unknown"}

        state = self.lifecycle.get_state(plugin_id)
        return {
            "plugin_id": plugin_id,
            "version": plugin.manifest.version,
            "state": state.value,
            "enabled": plugin.is_enabled,
            "health": record.health_status,
            "installed_at": record.installed_at,
        }

    def _update_metrics(self):
        enabled_count = len(self.registry.get_enabled())
        disabled_count = len(self.registry.get_disabled())
        PLUGIN_ENABLED_TOTAL.set(enabled_count)
        PLUGIN_DISABLED_TOTAL.set(disabled_count)
