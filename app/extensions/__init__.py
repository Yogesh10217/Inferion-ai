"""Plugin & Extension Framework Package."""

from app.extensions.exceptions import (
    ExtensionFrameworkException, ExtensionNotFoundException, InvalidExtensionManifestException,
    ExtensionSecurityViolationException, ExtensionDependencyConflictException,
    InvalidExtensionLifecycleTransition, ExtensionRuntimeExecutionException,
)
from app.extensions.extension import (
    ExtensionType, ExtensionRuntimeRequirements, ExtensionManifest, ExtensionVersion, Extension,
)
from app.extensions.extension_registry import ExtensionRegistry
from app.extensions.extension_loader import ExtensionLoader
from app.extensions.extension_runtime import IsolatedExtensionRuntime
from app.extensions.extension_permissions import ExtensionPermissionEngine
from app.extensions.extension_lifecycle import ExtensionLifecycleState, ExtensionLifecycleManager
from app.extensions.dependencies import ExtensionLockfile, DependencyResolver
from app.extensions.security import SecurityAnalysisReport, ExtensionSecurityEngine
from app.extensions.billing import ExtensionBillingRecord, ExtensionBillingTracker
from app.extensions.observability import ExtensionTraceContext, ExtensionMetricsCollector
from app.extensions.agent_extension import AgentCapabilityManifest, AgentTemplate, AgentExtensionAdapter
from app.extensions.workflow_template import WorkflowTemplate, WorkflowTemplateEngine
from app.extensions.mcp_package import MCPServerManifest, MCPPackage, MCPPackageManager
from app.extensions.manager import ExtensionManager

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
