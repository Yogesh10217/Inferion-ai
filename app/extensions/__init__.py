"""Plugin & Extension Framework Package."""

from app.extensions.agent_extension import AgentCapabilityManifest, AgentExtensionAdapter, AgentTemplate
from app.extensions.billing import ExtensionBillingRecord, ExtensionBillingTracker
from app.extensions.dependencies import DependencyResolver, ExtensionLockfile
from app.extensions.exceptions import (
    ExtensionDependencyConflictException,
    ExtensionFrameworkException,
    ExtensionNotFoundException,
    ExtensionRuntimeExecutionException,
    ExtensionSecurityViolationException,
    InvalidExtensionLifecycleTransition,
    InvalidExtensionManifestException,
)
from app.extensions.extension import (
    Extension,
    ExtensionManifest,
    ExtensionRuntimeRequirements,
    ExtensionType,
    ExtensionVersion,
)
from app.extensions.extension_lifecycle import ExtensionLifecycleManager, ExtensionLifecycleState
from app.extensions.extension_loader import ExtensionLoader
from app.extensions.extension_permissions import ExtensionPermissionEngine
from app.extensions.extension_registry import ExtensionRegistry
from app.extensions.extension_runtime import IsolatedExtensionRuntime
from app.extensions.manager import ExtensionManager
from app.extensions.mcp_package import MCPPackage, MCPPackageManager, MCPServerManifest
from app.extensions.observability import ExtensionMetricsCollector, ExtensionTraceContext
from app.extensions.security import ExtensionSecurityEngine, SecurityAnalysisReport
from app.extensions.workflow_template import WorkflowTemplate, WorkflowTemplateEngine

__all__ = [
    "ExtensionFrameworkException",
    "ExtensionNotFoundException",
    "InvalidExtensionManifestException",
    "ExtensionSecurityViolationException",
    "ExtensionDependencyConflictException",
    "InvalidExtensionLifecycleTransition",
    "ExtensionRuntimeExecutionException",
    "ExtensionType",
    "ExtensionRuntimeRequirements",
    "ExtensionManifest",
    "ExtensionVersion",
    "Extension",
    "ExtensionRegistry",
    "ExtensionLoader",
    "IsolatedExtensionRuntime",
    "ExtensionPermissionEngine",
    "ExtensionLifecycleState",
    "ExtensionLifecycleManager",
    "ExtensionLockfile",
    "DependencyResolver",
    "SecurityAnalysisReport",
    "ExtensionSecurityEngine",
    "ExtensionBillingRecord",
    "ExtensionBillingTracker",
    "ExtensionTraceContext",
    "ExtensionMetricsCollector",
    "AgentCapabilityManifest",
    "AgentTemplate",
    "AgentExtensionAdapter",
    "WorkflowTemplate",
    "WorkflowTemplateEngine",
    "MCPServerManifest",
    "MCPPackage",
    "MCPPackageManager",
    "ExtensionManager",
]
