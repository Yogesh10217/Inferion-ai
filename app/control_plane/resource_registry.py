"""Centralized Platform Resource Inventory & Registry."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.control_plane.exceptions import ResourceNotFoundException

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    MODEL = "MODEL"
    PROVIDER = "PROVIDER"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    DOCUMENT = "DOCUMENT"
    AGENT = "AGENT"
    AGENT_TEAM = "AGENT_TEAM"
    WORKFLOW = "WORKFLOW"
    TOOL = "TOOL"
    MCP_SERVER = "MCP_SERVER"
    MEMORY = "MEMORY"
    PLAN = "PLAN"
    AUTONOMOUS_EXECUTION = "AUTONOMOUS_EXECUTION"
    DIGITAL_WORKER = "DIGITAL_WORKER"
    API_KEY = "API_KEY"
    SECRET_REFERENCE = "SECRET_REFERENCE"
    FEATURE_FLAG = "FEATURE_FLAG"
    DEVELOPER = "DEVELOPER"
    DEVELOPER_PROJECT = "DEVELOPER_PROJECT"
    EXTENSION = "EXTENSION"
    EXTENSION_VERSION = "EXTENSION_VERSION"
    MARKETPLACE_ITEM = "MARKETPLACE_ITEM"
    MARKETPLACE_INSTALLATION = "MARKETPLACE_INSTALLATION"
    MCP_PACKAGE = "MCP_PACKAGE"
    WEBHOOK_SUBSCRIPTION = "WEBHOOK_SUBSCRIPTION"
    DATA_SOURCE = "DATA_SOURCE"
    DATA_CONNECTOR = "DATA_CONNECTOR"
    DATASET = "DATASET"
    DATA_ASSET = "DATA_ASSET"
    DATA_SCHEMA = "DATA_SCHEMA"
    DATA_SYNC = "DATA_SYNC"
    DATA_LINEAGE = "DATA_LINEAGE"
    DATA_POLICY = "DATA_POLICY"
    AI_ASSET = "AI_ASSET"
    AI_ASSET_VERSION = "AI_ASSET_VERSION"
    MODEL_VERSION = "MODEL_VERSION"
    PROMPT = "PROMPT"
    PROMPT_VERSION = "PROMPT_VERSION"
    EXPERIMENT = "EXPERIMENT"
    EVALUATION_DATASET = "EVALUATION_DATASET"
    EVALUATION_RUN = "EVALUATION_RUN"
    DEPLOYMENT = "DEPLOYMENT"
    RELEASE = "RELEASE"
    RELEASE_ARTIFACT = "RELEASE_ARTIFACT"
    ROLLBACK = "ROLLBACK"
    DRIFT_EVENT = "DRIFT_EVENT"
    COST_LEDGER = "COST_LEDGER"
    BUDGET = "BUDGET"
    COST_FORECAST = "COST_FORECAST"
    COST_ANOMALY = "COST_ANOMALY"
    OPTIMIZATION_RECOMMENDATION = "OPTIMIZATION_RECOMMENDATION"
    OPTIMIZATION_EXECUTION = "OPTIMIZATION_EXECUTION"
    SAVINGS_RECORD = "SAVINGS_RECORD"
    CAPACITY_PLAN = "CAPACITY_PLAN"
    PRICING_CATALOG = "PRICING_CATALOG"
    CHARGEBACK_REPORT = "CHARGEBACK_REPORT"
    TELEMETRY_STREAM = "TELEMETRY_STREAM"
    SERVICE_TOPOLOGY = "SERVICE_TOPOLOGY"
    SERVICE_LEVEL_OBJECTIVE = "SERVICE_LEVEL_OBJECTIVE"
    ERROR_BUDGET = "ERROR_BUDGET"
    ALERT_RULE = "ALERT_RULE"
    ALERT = "ALERT"
    INCIDENT = "INCIDENT"
    ROOT_CAUSE_ANALYSIS = "ROOT_CAUSE_ANALYSIS"
    RUNBOOK = "RUNBOOK"
    RUNBOOK_EXECUTION = "RUNBOOK_EXECUTION"
    REMEDIATION_PLAN = "REMEDIATION_PLAN"
    REMEDIATION_EXECUTION = "REMEDIATION_EXECUTION"
    FAILURE_PREDICTION = "FAILURE_PREDICTION"
    POSTMORTEM = "POSTMORTEM"
    GOVERNANCE_FRAMEWORK = "GOVERNANCE_FRAMEWORK"
    GOVERNANCE_CONTROL = "GOVERNANCE_CONTROL"
    RISK = "RISK"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    COMPLIANCE_FRAMEWORK = "COMPLIANCE_FRAMEWORK"
    COMPLIANCE_REQUIREMENT = "COMPLIANCE_REQUIREMENT"
    COMPLIANCE_ASSESSMENT = "COMPLIANCE_ASSESSMENT"
    COMPLIANCE_FINDING = "COMPLIANCE_FINDING"
    GOVERNANCE_EVIDENCE = "GOVERNANCE_EVIDENCE"
    GOVERNANCE_DECISION = "GOVERNANCE_DECISION"
    GOVERNANCE_VIOLATION = "GOVERNANCE_VIOLATION"
    TRUST_ASSESSMENT = "TRUST_ASSESSMENT"
    AUTONOMY_POLICY = "AUTONOMY_POLICY"
    GOVERNANCE_REMEDIATION = "GOVERNANCE_REMEDIATION"
    IDENTITY = "IDENTITY"
    ROLE = "ROLE"
    PERMISSION = "PERMISSION"
    ACCESS_POLICY = "ACCESS_POLICY"
    AUTH_SESSION = "AUTH_SESSION"
    CREDENTIAL = "CREDENTIAL"
    PRIVILEGED_ACCESS = "PRIVILEGED_ACCESS"
    WORKLOAD_IDENTITY = "WORKLOAD_IDENTITY"
    IDENTITY_RISK_EVENT = "IDENTITY_RISK_EVENT"
    ACCESS_REVIEW = "ACCESS_REVIEW"
    DELEGATED_AUTHORIZATION = "DELEGATED_AUTHORIZATION"
    ZERO_TRUST_POLICY = "ZERO_TRUST_POLICY"
    WORKFLOW_DEFINITION = "WORKFLOW_DEFINITION"
    WORKFLOW_VERSION = "WORKFLOW_VERSION"
    # Phase 5.18 Resource Types
    ORCHESTRATION_WORKFLOW = "ORCHESTRATION_WORKFLOW"
    ORCHESTRATION_EXECUTION = "ORCHESTRATION_EXECUTION"
    HUMAN_TASK = "HUMAN_TASK"
    ENTERPRISE_CASE = "ENTERPRISE_CASE"
    EXECUTION_ROUTE = "EXECUTION_ROUTE"
    AGENT_ORCHESTRATION = "AGENT_ORCHESTRATION"
    DECISION_TABLE = "DECISION_TABLE"
    ORCHESTRATION_EVENT = "ORCHESTRATION_EVENT"
    SAGA_TRANSACTION = "SAGA_TRANSACTION"
    WORKFLOW_GOVERNANCE = "WORKFLOW_GOVERNANCE"
    PROCESS_ANALYTICS = "PROCESS_ANALYTICS"
    ORCHESTRATION_METRICS = "ORCHESTRATION_METRICS"

    # Phase 5.19 Resource Types
    KNOWLEDGE_ITEM = "KNOWLEDGE_ITEM"
    KNOWLEDGE_VERSION = "KNOWLEDGE_VERSION"
    KNOWLEDGE_SOURCE = "KNOWLEDGE_SOURCE"
    KNOWLEDGE_GRAPH = "KNOWLEDGE_GRAPH"
    KNOWLEDGE_NODE = "KNOWLEDGE_NODE"
    KNOWLEDGE_EDGE = "KNOWLEDGE_EDGE"
    CONTEXT = "CONTEXT"
    CONTEXT_POLICY = "CONTEXT_POLICY"
    KNOWLEDGE_CONFLICT = "KNOWLEDGE_CONFLICT"
    PROVENANCE_RECORD = "PROVENANCE_RECORD"






class PlatformResource(BaseModel):
    """Universal platform resource entry."""

    resource_id: str
    resource_type: ResourceType
    name: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    owner_id: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "ACTIVE"
    version: str = "1.0.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResourceRegistry:
    """Central registry keeping inventory of all assets across all 16 platform subsystems."""

    def __init__(self) -> None:
        self._resources: Dict[str, PlatformResource] = {}
        self._type_index: Dict[ResourceType, List[str]] = {t: [] for t in ResourceType}

    def register_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        name: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        owner_id: str = "system",
        status: str = "ACTIVE",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PlatformResource:
        """Register or update a managed platform resource."""
        res = PlatformResource(
            resource_id=resource_id,
            resource_type=resource_type,
            name=name,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            owner_id=owner_id,
            status=status,
            version=version,
            metadata=metadata or {},
        )
        self._resources[resource_id] = res

        if resource_id not in self._type_index[resource_type]:
            self._type_index[resource_type].append(resource_id)

        logger.info(f"[RESOURCE REGISTRY] Registered resource '{name}' (ID: {resource_id}, Type: {resource_type.value})")
        return res

    def unregister_resource(self, resource_id: str) -> bool:
        """Remove a resource from the registry."""
        if resource_id not in self._resources:
            raise ResourceNotFoundException(resource_id)

        res = self._resources[resource_id]
        if resource_id in self._type_index[res.resource_type]:
            self._type_index[res.resource_type].remove(resource_id)
        del self._resources[resource_id]

        logger.info(f"[RESOURCE REGISTRY] Unregistered resource '{resource_id}'")
        return True

    def get_resource(self, resource_id: str) -> PlatformResource:
        """Get resource by ID."""
        res = self._resources.get(resource_id)
        if not res:
            raise ResourceNotFoundException(resource_id)
        return res

    def list_resources(
        self,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
    ) -> List[PlatformResource]:
        """List resources matching scope filters."""
        res_list = list(self._resources.values())
        if tenant_id:
            res_list = [r for r in res_list if r.tenant_id == tenant_id]
        if organization_id:
            res_list = [r for r in res_list if r.organization_id == organization_id]
        if workspace_id:
            res_list = [r for r in res_list if r.workspace_id == workspace_id]
        if resource_type:
            res_list = [r for r in res_list if r.resource_type == resource_type]
        return res_list

    def search_resources(self, query: str, tenant_id: Optional[str] = None) -> List[PlatformResource]:
        """Search resources by name or ID snippet."""
        q_norm = query.lower()
        res_list = self.list_resources(tenant_id=tenant_id)
        return [r for r in res_list if q_norm in r.name.lower() or q_norm in r.resource_id.lower()]

    def get_resource_owner(self, resource_id: str) -> str:
        """Get owner ID of resource."""
        return self.get_resource(resource_id).owner_id

    def get_resource_usage(self, resource_id: str) -> Dict[str, Any]:
        """Get resource usage metadata."""
        res = self.get_resource(resource_id)
        return {
            "resource_id": resource_id,
            "status": res.status,
            "version": res.version,
            "usage_count": res.metadata.get("usage_count", 0),
        }
