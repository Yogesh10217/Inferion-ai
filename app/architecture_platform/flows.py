"""System Flow Intelligence & Multi-Node Flow Mapping Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.architecture_platform.nodes import ArchitectureNodeType


class FlowStepType(str, Enum):
    ENTRY_POINT = "ENTRY_POINT"
    APPLICATION_DISPATCH = "APPLICATION_DISPATCH"
    AGENT_REASONING = "AGENT_REASONING"
    WORKFLOW_STEP = "WORKFLOW_STEP"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    INTEGRATION_CALL = "INTEGRATION_CALL"
    DATA_ACCESS = "DATA_ACCESS"
    RESPONSE_GENERATION = "RESPONSE_GENERATION"


class FlowStep(BaseModel):
    step_number: int
    step_type: FlowStepType
    node_id: str
    node_name: str
    node_type: ArchitectureNodeType
    classification_level: str = "CONFIDENTIAL"
    policy_decision: str = "ALLOW"
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Secret-sanitized metadata only


class ArchitectureFlow(BaseModel):
    flow_id: str = Field(default_factory=lambda: f"flow_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    description: str = ""
    steps: List[FlowStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataFlow(BaseModel):
    flow_id: str
    tenant_id: str
    source_node_id: str
    target_node_id: str
    data_classification: str = "CONFIDENTIAL"
    encryption_status: str = "ENCRYPTED_IN_TRANSIT"


class ControlFlow(BaseModel):
    flow_id: str
    tenant_id: str
    trigger_type: str = "API_REQUEST"
    initiator_id: str = "system"


class AIExecutionFlow(BaseModel):
    flow_id: str
    tenant_id: str
    agent_id: str
    model_id: str
    tools_used: List[str] = Field(default_factory=list)


class FlowManager:
    """Manages system flow mapping across applications, agents, workflows, models, tools, and data assets."""

    def __init__(self) -> None:
        self._flows: Dict[str, Dict[str, ArchitectureFlow]] = {}  # tenant_id -> {flow_id -> ArchitectureFlow}

    def create_flow(
        self,
        tenant_id: str,
        name: str,
        steps: List[FlowStep],
        description: str = "",
    ) -> ArchitectureFlow:
        flow = ArchitectureFlow(
            tenant_id=tenant_id,
            name=name,
            steps=steps,
            description=description,
        )
        if tenant_id not in self._flows:
            self._flows[tenant_id] = {}
        self._flows[tenant_id][flow.flow_id] = flow
        return flow

    def get_flow(self, flow_id: str, tenant_id: str) -> ArchitectureFlow:
        tenant_flows = self._flows.get(tenant_id, {})
        flow = tenant_flows.get(flow_id)
        if not flow:
            raise KeyError(f"Flow '{flow_id}' not found for tenant '{tenant_id}'.")
        return flow

    def list_flows(self, tenant_id: str) -> List[ArchitectureFlow]:
        return list(self._flows.get(tenant_id, {}).values())
