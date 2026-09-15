"""
High-Level Tool Platform Coordinator & Lifecycle Manager
"""

import logging
from typing import List, Optional

from app.tools.tool_registry import ToolRegistry
from app.tools.tool_executor import ToolExecutor
from app.tools.tool_permissions import ToolPermissionEngine
from app.tools.tool_audit import ToolAuditLogger
from app.tools.tool_billing import ToolBillingTracker
from app.tools.tool import BaseTool, ToolMetadata

logger = logging.getLogger(__name__)


class ToolManager:
    """Manager coordinating tool registration, execution, auditing, security, and MCP integration."""

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        executor: Optional[ToolExecutor] = None,
        permission_engine: Optional[ToolPermissionEngine] = None,
        audit_logger: Optional[ToolAuditLogger] = None,
        billing_tracker: Optional[ToolBillingTracker] = None,
    ):
        self.registry = registry or ToolRegistry()
        self.permission_engine = permission_engine or ToolPermissionEngine()
        self.audit_logger = audit_logger or ToolAuditLogger()
        self.billing_tracker = billing_tracker or ToolBillingTracker()
        self.executor = executor or ToolExecutor(
            registry=self.registry,
            permission_engine=self.permission_engine,
            audit_logger=self.audit_logger,
            billing_tracker=self.billing_tracker,
        )

    def register_tool(self, tool: BaseTool, tenant_id: Optional[str] = None) -> None:
        self.registry.register_tool(tool, tenant_id)

    def unregister_tool(self, name: str, tenant_id: str = "global", version: Optional[str] = None) -> bool:
        return self.registry.unregister_tool(name, tenant_id, version)

    def get_tool(self, name: str, tenant_id: str = "global", version: Optional[str] = None) -> BaseTool:
        return self.registry.get_tool(name, tenant_id, version)

    def list_tools(self, tenant_id: str = "global") -> List[ToolMetadata]:
        return self.registry.list_tools(tenant_id=tenant_id)
