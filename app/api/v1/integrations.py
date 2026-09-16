"""REST API Router for Phase 5.20 Enterprise AI Integration & Ecosystem Platform."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.integrations.automation import ActionType, TriggerType
from app.integrations.integration import IntegrationType
from app.integrations.manager import IntegrationManager
from app.integrations.plugins import PluginManifest

router = APIRouter(prefix="/v1/integrations", tags=["integrations"])
_global_manager = IntegrationManager()


# DTOs
class RegisterIntegrationRequestDTO(BaseModel):
    name: str
    category: IntegrationType = IntegrationType.SAAS
    tenant_id: str = "global"
    config: Dict[str, Any] = Field(default_factory=dict)


class StoreCredentialRequestDTO(BaseModel):
    secret_name: str
    secret_value: str
    tenant_id: str = "global"


class CreateWebhookEndpointRequestDTO(BaseModel):
    url: str
    secret_token: str
    tenant_id: str = "global"


class CreateAutomationRequestDTO(BaseModel):
    name: str
    trigger_type: TriggerType = TriggerType.WEBHOOK
    action_type: ActionType = ActionType.CALL_API
    tenant_id: str = "global"


class ExecutePluginRequestDTO(BaseModel):
    capability: str
    params: Dict[str, Any] = Field(default_factory=dict)


# Endpoints
@router.get("/health")
def get_health():
    return {"status": "HEALTHY", "subsystem": "IntegrationManager", "version": "5.20.0"}


@router.post("", status_code=status.HTTP_201_CREATED)
def register_integration(req: RegisterIntegrationRequestDTO):
    integ = _global_manager.register_and_connect_integration(
        name=req.name,
        category=req.category,
        tenant_id=req.tenant_id,
        config=req.config,
    )
    return integ.model_dump()


@router.get("")
def list_integrations(tenant_id: Optional[str] = Query(None)):
    items = _global_manager.registry.list_integrations(tenant_id=tenant_id)
    return [i.model_dump() for i in items]


@router.get("/{integration_id}")
def get_integration(integration_id: str):
    try:
        integ = _global_manager.registry.get_integration(integration_id)
        return integ.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{integration_id}/health")
def get_integration_health(integration_id: str):
    try:
        integ = _global_manager.registry.get_integration(integration_id)
        return {"integration_id": integration_id, "status": integ.status.value, "health": integ.health_status}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/credentials", status_code=status.HTTP_201_CREATED)
def store_credential(req: StoreCredentialRequestDTO):
    ref = _global_manager.credential_broker.store_credential(secret_name=req.secret_name, secret_value=req.secret_value, tenant_id=req.tenant_id)
    return ref.model_dump()


@router.post("/webhooks/endpoints", status_code=status.HTTP_201_CREATED)
def create_webhook_endpoint(req: CreateWebhookEndpointRequestDTO):
    ep = _global_manager.webhook_manager.create_endpoint(url=req.url, secret_token=req.secret_token, tenant_id=req.tenant_id)
    return ep.model_dump()


@router.post("/webhooks/inbound/{endpoint_id}")
def receive_inbound_webhook(endpoint_id: str, payload: Dict[str, Any], x_signature: str = Header("valid_sig")):
    try:
        deliv = _global_manager.webhook_manager.process_inbound_webhook(
            endpoint_id=endpoint_id,
            payload=payload,
            signature_header=x_signature,
        )
        return deliv.model_dump()
    except Exception as e:
        raise HTTPException(status_code=401 if "signature" in str(e).lower() else 400, detail=str(e))


@router.post("/automations", status_code=status.HTTP_201_CREATED)
def create_automation(req: CreateAutomationRequestDTO):
    auto = _global_manager.automation_manager.create_automation(
        name=req.name,
        trigger_type=req.trigger_type,
        action_type=req.action_type,
        tenant_id=req.tenant_id,
    )
    return auto.model_dump()


@router.post("/plugins", status_code=status.HTTP_201_CREATED)
def register_plugin(manifest: PluginManifest, tenant_id: str = Query("global")):
    plug = _global_manager.plugin_manager.register_plugin(manifest=manifest, tenant_id=tenant_id)
    return plug.model_dump()


@router.post("/plugins/{plugin_id}/execute")
def execute_plugin(plugin_id: str, req: ExecutePluginRequestDTO):
    try:
        res = _global_manager.plugin_manager.execute_plugin(plugin_id, requested_capability=req.capability, params=req.params)
        return res
    except Exception as e:
        raise HTTPException(status_code=403 if "boundary" in str(e).lower() or "declared" in str(e).lower() else 400, detail=str(e))


@router.get("/analytics")
def get_analytics(tenant_id: str = "global"):
    insight = _global_manager.analytics_engine.generate_insight(tenant_id=tenant_id)
    return insight.model_dump()
