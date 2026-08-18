"""
Thread-safe, Multi-tenant, RBAC & Version-aware Tool Registry
"""

import threading
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from app.tools.tool import BaseTool, ToolMetadata, ToolCategory, ToolDefinition
from app.tools.exceptions import ToolNotFoundException, ToolValidationError, ToolPermissionDenied

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry storing and resolving tools across multi-tenant boundaries."""

    def __init__(self):
        self._lock = threading.RLock()
        # Key format: (tenant_id, tool_name, version) -> BaseTool
        self._tools: Dict[Tuple[str, str, str], BaseTool] = {}
        # Index for latest version: (tenant_id, tool_name) -> version
        self._latest_versions: Dict[Tuple[str, str], str] = {}

    def register_tool(self, tool: BaseTool, tenant_id: Optional[str] = None) -> None:
        """Register a tool instance for a given tenant."""
        with self._lock:
            tid = tenant_id or tool.metadata.tenant_id or "global"
            name = tool.metadata.name
            version = tool.metadata.version

            # Set tenant_id on metadata
            tool.metadata.tenant_id = tid

            key = (tid, name, version)
            self._tools[key] = tool

            # Update latest version pointer
            self._latest_versions[(tid, name)] = version
            logger.info(f"Registered tool '{name}' (v{version}) for tenant '{tid}'")

    def unregister_tool(self, name: str, tenant_id: str = "global", version: Optional[str] = None) -> bool:
        """Unregister a tool for a given tenant and optional version."""
        with self._lock:
            if version:
                key = (tenant_id, name, version)
                if key in self._tools:
                    del self._tools[key]
                    if self._latest_versions.get((tenant_id, name)) == version:
                        del self._latest_versions[(tenant_id, name)]
                    logger.info(f"Unregistered tool '{name}' (v{version}) for tenant '{tenant_id}'")
                    return True
                return False

            # Delete all versions of the tool for this tenant
            keys_to_del = [k for k in self._tools if k[0] == tenant_id and k[1] == name]
            if not keys_to_del:
                return False

            for k in keys_to_del:
                del self._tools[k]
            if (tenant_id, name) in self._latest_versions:
                del self._latest_versions[(tenant_id, name)]

            logger.info(f"Unregistered all versions of tool '{name}' for tenant '{tenant_id}'")
            return True

    def get_tool(self, name: str, tenant_id: str = "global", version: Optional[str] = None) -> BaseTool:
        """Retrieve a registered tool by name, tenant, and optional version."""
        with self._lock:
            # 1. Check specified tenant
            if version:
                key = (tenant_id, name, version)
                if key in self._tools:
                    return self._tools[key]
            else:
                v = self._latest_versions.get((tenant_id, name))
                if v and (tenant_id, name, v) in self._tools:
                    return self._tools[(tenant_id, name, v)]

            # 2. Fallback to 'global' tenant
            if tenant_id != "global":
                if version:
                    key = ("global", name, version)
                    if key in self._tools:
                        return self._tools[key]
                else:
                    v = self._latest_versions.get(("global", name))
                    if v and ("global", name, v) in self._tools:
                        return self._tools[("global", name, v)]

            raise ToolNotFoundException(f"Tool '{name}' (version: {version or 'latest'}) not found for tenant '{tenant_id}'")

    def tool_exists(self, name: str, tenant_id: str = "global", version: Optional[str] = None) -> bool:
        """Check if a tool is registered."""
        try:
            self.get_tool(name, tenant_id, version)
            return True
        except ToolNotFoundException:
            return False

    def list_tools(
        self,
        tenant_id: str = "global",
        category: Optional[Union[str, ToolCategory]] = None,
        tags: Optional[List[str]] = None,
        user_role: Optional[str] = None,
        user_scopes: Optional[List[str]] = None,
    ) -> List[ToolMetadata]:
        """List registered tools accessible to tenant, role, and scopes."""
        with self._lock:
            matched_tools: Dict[str, BaseTool] = {}

            # Gather tools for tenant_id and global
            for (tid, name, ver), tool in self._tools.items():
                if tid not in (tenant_id, "global"):
                    continue

                # Filter by category
                if category:
                    cat_val = category.value if isinstance(category, ToolCategory) else str(category)
                    if tool.metadata.category.value != cat_val:
                        continue

                # Filter by tags
                if tags:
                    if not any(tag in tool.metadata.tags for tag in tags):
                        continue

                # Filter by RBAC user_scopes if specified
                if user_scopes is not None and "admin" not in (user_scopes or []):
                    req_scopes = tool.metadata.scopes
                    if req_scopes and not any(s in user_scopes for s in req_scopes):
                        continue

                # Keep latest version per name (tenant specific overrides global)
                if name not in matched_tools or tid == tenant_id:
                    matched_tools[name] = tool

            return [t.metadata for t in matched_tools.values()]

    def search_tools(self, query: str, tenant_id: str = "global") -> List[ToolMetadata]:
        """Search tools by name or description keywords."""
        query_lower = query.lower()
        all_tools = self.list_tools(tenant_id=tenant_id)
        results = []
        for meta in all_tools:
            if query_lower in meta.name.lower() or query_lower in meta.description.lower():
                results.append(meta)
        return results

    def validate_tool(self, tool: BaseTool) -> bool:
        """Validate tool schema metadata."""
        if not tool.metadata.name:
            raise ToolValidationError("Tool metadata must specify a valid name")
        if not tool.metadata.description:
            raise ToolValidationError("Tool metadata must specify a description")
        if not isinstance(tool.metadata.parameters_schema, dict):
            raise ToolValidationError("Tool parameters_schema must be a valid dictionary")
        return True
