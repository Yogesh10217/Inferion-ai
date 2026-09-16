from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from .plugin_manager import PluginManager

router = APIRouter(prefix="/v1/plugins", tags=["plugins"])

# Global PluginManager instance for API dependency injection
_global_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    global _global_plugin_manager
    if _global_plugin_manager is None:
        _global_plugin_manager = PluginManager()
    return _global_plugin_manager


def set_plugin_manager(manager: PluginManager):
    global _global_plugin_manager
    _global_plugin_manager = manager


class InstallPluginSchema(BaseModel):
    plugin_id: str


@router.get("/")
async def list_plugins(manager: PluginManager = Depends(get_plugin_manager)):
    """List all registered plugins."""
    plugins = manager.registry.get_all()
    result = []
    for p in plugins:
        health = manager.get_plugin_health(p.manifest.id)
        result.append({
            "id": p.manifest.id,
            "name": p.manifest.name,
            "version": p.manifest.version,
            "description": p.manifest.description,
            "author": p.manifest.author,
            "enabled": p.is_enabled,
            "health": health.get("health", "healthy"),
            "state": health.get("state", "UNKNOWN"),
        })
    return {"plugins": result}


@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str, manager: PluginManager = Depends(get_plugin_manager)):
    """Get details for a specific plugin."""
    plugin = manager.registry.get(plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found",
        )
    health = manager.get_plugin_health(plugin_id)
    return {
        "manifest": plugin.manifest.dict(),
        "enabled": plugin.is_enabled,
        "health": health,
    }


@router.post("/install", status_code=status.HTTP_201_CREATED)
async def install_plugin(
    data: InstallPluginSchema,
    manager: PluginManager = Depends(get_plugin_manager),
):
    """Install a plugin by ID from configured store."""
    try:
        plugin = await manager.install_plugin(data.plugin_id)
        return {"status": "installed", "plugin_id": plugin.manifest.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to install plugin '{data.plugin_id}': {str(e)}",
        )


@router.post("/uninstall/{plugin_id}")
@router.delete("/{plugin_id}")
async def uninstall_plugin(plugin_id: str, manager: PluginManager = Depends(get_plugin_manager)):
    """Uninstall and remove a plugin."""
    plugin = manager.registry.get(plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found",
        )
    await manager.uninstall_plugin(plugin_id)
    return {"status": "uninstalled", "plugin_id": plugin_id}


@router.post("/enable/{plugin_id}")
@router.patch("/{plugin_id}/enable")
async def enable_plugin(plugin_id: str, manager: PluginManager = Depends(get_plugin_manager)):
    """Enable a registered plugin."""
    try:
        await manager.enable_plugin(plugin_id)
        return {"status": "enabled", "plugin_id": plugin_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to enable plugin '{plugin_id}': {str(e)}",
        )


@router.post("/disable/{plugin_id}")
@router.patch("/{plugin_id}/disable")
async def disable_plugin(plugin_id: str, manager: PluginManager = Depends(get_plugin_manager)):
    """Disable an enabled plugin."""
    try:
        await manager.disable_plugin(plugin_id)
        return {"status": "disabled", "plugin_id": plugin_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to disable plugin '{plugin_id}': {str(e)}",
        )


@router.post("/reload/{plugin_id}")
@router.post("/{plugin_id}/reload")
async def reload_plugin(plugin_id: str, manager: PluginManager = Depends(get_plugin_manager)):
    """Reload a plugin."""
    try:
        plugin = await manager.reload_plugin(plugin_id)
        return {"status": "reloaded", "plugin_id": plugin.manifest.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reload plugin '{plugin_id}': {str(e)}",
        )


@router.get("/{plugin_id}/health")
async def plugin_health(plugin_id: str, manager: PluginManager = Depends(get_plugin_manager)):
    """Get health and diagnostic status of a plugin."""
    health = manager.get_plugin_health(plugin_id)
    if health.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found",
        )
    return health
