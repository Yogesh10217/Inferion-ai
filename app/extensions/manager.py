"""Master Extension Manager unifying framework components."""

import logging
from typing import Any, Dict

from app.extensions.agent_extension import AgentExtensionAdapter
from app.extensions.billing import ExtensionBillingTracker
from app.extensions.dependencies import DependencyResolver
from app.extensions.extension_lifecycle import ExtensionLifecycleManager
from app.extensions.extension_loader import ExtensionLoader
from app.extensions.extension_permissions import ExtensionPermissionEngine
from app.extensions.extension_registry import ExtensionRegistry
from app.extensions.extension_runtime import IsolatedExtensionRuntime
from app.extensions.mcp_package import MCPPackageManager
from app.extensions.observability import ExtensionMetricsCollector
from app.extensions.security import ExtensionSecurityEngine
from app.extensions.workflow_template import WorkflowTemplateEngine

logger = logging.getLogger(__name__)


class ExtensionManager:
    """Master Manager orchestrating extension registration, loading, sandboxed execution, and lifecycle."""

    def __init__(self) -> None:
        self.registry = ExtensionRegistry()
        self.loader = ExtensionLoader()
        self.runtime = IsolatedExtensionRuntime()
        self.permission_engine = ExtensionPermissionEngine()
        self.lifecycle_manager = ExtensionLifecycleManager()
        self.dependency_resolver = DependencyResolver()
        self.security_engine = ExtensionSecurityEngine()
        self.billing_tracker = ExtensionBillingTracker()
        self.metrics_collector = ExtensionMetricsCollector()

        self.agent_adapter = AgentExtensionAdapter()
        self.workflow_template_engine = WorkflowTemplateEngine()
        self.mcp_package_manager = MCPPackageManager()

        logger.info("[EXTENSION MANAGER MASTER] ExtensionManager initialized with all 12 extensibility framework modules")

    def get_summary(self) -> Dict[str, Any]:
        """Aggregate extension framework summary."""
        exts = self.registry.list_extensions()
        enabled = self.registry.list_extensions(enabled_only=True)

        return {
            "total_extensions": len(exts),
            "enabled_extensions": len(enabled),
            "metrics": self.metrics_collector.get_metrics_summary(),
        }
