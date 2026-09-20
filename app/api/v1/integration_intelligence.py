"""REST API Router for Integration Intelligence Platform (Phase 5.40)."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.integration_intelligence.connectors import ConnectorCapability, ConnectorType
from app.integration_intelligence.endpoints import EndpointProtocol, EndpointType
from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    HighRiskIntegrationRequiresApprovalException,
    IntegrationIntelligenceException,
)
from app.integration_intelligence.manager import IntegrationIntelligenceManager
from app.integration_intelligence.workflows import WorkflowStep, WorkflowTrigger, WorkflowType

router = APIRouter(prefix="/integrations", tags=["Integration Intelligence"])
manager = IntegrationIntelligenceManager()


def get_tenant_id(x_tenant_id: Optional[str] = Header("default_tenant")) -> str:
    return x_tenant_id or "default_tenant"


class RegisterConnectorRequest(BaseModel):
    name: str
    connector_type: ConnectorType = ConnectorType.API
    external_system_id: str
    provider_name: str
    base_endpoint_url: str
    auth_type: str = "OAUTH2"
    secret_reference_id: Optional[str] = None
    capabilities: List[ConnectorCapability] = [ConnectorCapability.READ]


class RegisterEndpointRequest(BaseModel):
    connector_id: str
    name: str
    endpoint_type: EndpointType = EndpointType.REST_API
    path_or_topic: str
    protocol: EndpointProtocol = EndpointProtocol.HTTP_HTTPS


class CreateWorkflowRequest(BaseModel):
    name: str
    workflow_type: WorkflowType = WorkflowType.SYNC_API
    trigger: WorkflowTrigger = WorkflowTrigger.API_INVOCATION
    steps: List[Dict[str, Any]] = []


class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    idempotency_key: str
    replay_token: Optional[str] = None
    requires_approval: bool = False


@router.post("/connectors")
def register_connector(req: RegisterConnectorRequest, tenant_id: str = Depends(get_tenant_id)):
    try:
        conn = manager.connector_manager.register_connector(
            tenant_id=tenant_id,
            name=req.name,
            connector_type=req.connector_type,
            external_system_id=req.external_system_id,
            provider_name=req.provider_name,
            base_endpoint_url=req.base_endpoint_url,
            capabilities=req.capabilities,
            auth_type=req.auth_type,
            secret_reference_id=req.secret_reference_id,
        )
        return conn.model_dump(mode="json")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/connectors/{connector_id}")
def get_connector(connector_id: str, tenant_id: str = Depends(get_tenant_id)):
    try:
        conn = manager.connector_manager.get_connector(tenant_id, connector_id)
        return conn.model_dump(mode="json")
    except CrossTenantIntegrationAccessException:
        raise HTTPException(status_code=404, detail="Connector not found")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/endpoints")
def register_endpoint(req: RegisterEndpointRequest, tenant_id: str = Depends(get_tenant_id)):
    try:
        ep = manager.endpoint_manager.register_endpoint(
            tenant_id=tenant_id,
            connector_id=req.connector_id,
            name=req.name,
            endpoint_type=req.endpoint_type,
            path_or_topic=req.path_or_topic,
            protocol=req.protocol,
        )
        return ep.model_dump(mode="json")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workflows")
def create_workflow(req: CreateWorkflowRequest, tenant_id: str = Depends(get_tenant_id)):
    try:
        steps = [WorkflowStep(**s) for s in req.steps]
        wf = manager.workflow_manager.create_workflow(
            tenant_id=tenant_id,
            name=req.name,
            workflow_type=req.workflow_type,
            trigger=req.trigger,
            steps=steps,
        )
        return wf.model_dump(mode="json")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str, tenant_id: str = Depends(get_tenant_id)):
    try:
        wf = manager.workflow_manager.get_workflow(tenant_id, workflow_id)
        return wf.model_dump(mode="json")
    except CrossTenantIntegrationAccessException:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/executions")
def request_execution(req: ExecuteWorkflowRequest, tenant_id: str = Depends(get_tenant_id)):
    try:
        exec_obj = manager.execution_manager.request_execution(
            tenant_id=tenant_id,
            workflow_id=req.workflow_id,
            idempotency_key=req.idempotency_key,
            replay_token=req.replay_token,
            requires_approval=req.requires_approval,
        )
        return exec_obj.model_dump(mode="json")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/executions/{execution_id}/delegate")
def delegate_execution(execution_id: str, tenant_id: str = Depends(get_tenant_id)):
    try:
        del_req = manager.execution_manager.delegate_execution(tenant_id, execution_id)
        return del_req.model_dump(mode="json")
    except HighRiskIntegrationRequiresApprovalException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CrossTenantIntegrationAccessException:
        raise HTTPException(status_code=404, detail="Execution not found")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics/report")
def get_analytics_report(tenant_id: str = Depends(get_tenant_id)):
    try:
        report = manager.analytics_engine.generate_report(tenant_id=tenant_id)
        return report.model_dump(mode="json")
    except IntegrationIntelligenceException as e:
        raise HTTPException(status_code=400, detail=str(e))
