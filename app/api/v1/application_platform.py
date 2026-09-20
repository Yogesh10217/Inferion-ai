"""FastAPI REST API Router for Phase 5.22 Enterprise AI Application Platform."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.application_platform.application import ApplicationConfiguration, ApplicationStatus, ApplicationType
from app.application_platform.exceptions import (
    ApplicationNotFoundException,
    ApplicationVersionNotFoundException,
    ExecutionCancelledException,
    GovernanceBlockedException,
)
from app.application_platform.feedback import FeedbackType
from app.application_platform.interactions import InteractionType
from app.application_platform.manager import ApplicationPlatformManager
from app.application_platform.runtime import ApplicationRuntime

router = APIRouter(prefix="/applications", tags=["Application Platform"])

_global_app_platform = ApplicationPlatformManager()


def get_application_platform() -> ApplicationPlatformManager:
    return _global_app_platform


class CreateApplicationRequest(BaseModel):
    name: str
    app_type: ApplicationType = ApplicationType.CUSTOM
    description: str = ""
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class UpdateApplicationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ApplicationStatus] = None


class CreateVersionRequest(BaseModel):
    version: str = "1.0.0"
    tenant_id: str = "global"
    configuration: Optional[ApplicationConfiguration] = None
    composition_references: List[str] = Field(default_factory=list)


class PromoteVersionRequest(BaseModel):
    target_status: ApplicationStatus
    tenant_id: str = "global"


class ExecuteApplicationRequest(BaseModel):
    tenant_id: str = "global"
    version_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    identity_id: str = "anonymous"
    environment: str = "PRODUCTION"


class CancelExecutionRequest(BaseModel):
    execution_id: str
    reason: str = "Cancelled via API"


class CreateInteractionRequest(BaseModel):
    tenant_id: str = "global"
    conversation_id: str
    user_input: str
    interaction_type: InteractionType = InteractionType.CHAT


class CreateFeatureRequest(BaseModel):
    tenant_id: str = "global"
    feature_key: str
    default_value: Any = True


class EvaluateFeatureRequest(BaseModel):
    tenant_id: str = "global"
    feature_key: str
    context: Dict[str, Any] = Field(default_factory=dict)


class SubmitFeedbackRequest(BaseModel):
    tenant_id: str = "global"
    execution_id: str
    feedback_type: FeedbackType = FeedbackType.POSITIVE
    score: Optional[float] = None
    comment: str = ""
    corrected_output: str = ""


@router.get("/health", status_code=status.HTTP_200_OK)
def application_platform_health(
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    return manager.get_platform_summary()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_application(
    req: CreateApplicationRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    app = manager.registry.create_application(
        tenant_id=req.tenant_id,
        name=req.name,
        app_type=req.app_type,
        description=req.description,
        organization_id=req.organization_id,
        workspace_id=req.workspace_id,
        tags=req.tags,
    )
    return app.model_dump(mode="json")


@router.get("")
def list_applications(
    tenant_id: str = Query("global"),
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    apps = manager.registry.list_applications(tenant_id)
    return [a.model_dump(mode="json") for a in apps]


@router.get("/{application_id}")
def get_application(
    application_id: str,
    tenant_id: str = Query("global"),
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    try:
        app = manager.registry.get_application(application_id, tenant_id)
        return app.model_dump(mode="json")
    except ApplicationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{application_id}")
def update_application(
    application_id: str,
    req: UpdateApplicationRequest,
    tenant_id: str = Query("global"),
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    try:
        app = manager.registry.get_application(application_id, tenant_id)
        if req.name is not None:
            app.name = req.name
        if req.description is not None:
            app.description = req.description
        if req.status is not None:
            app.status = req.status
        saved = manager.repository.save_application(app.model_dump(mode="json"))
        return saved
    except ApplicationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{application_id}/versions", status_code=status.HTTP_201_CREATED)
def create_version(
    application_id: str,
    req: CreateVersionRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    try:
        ver = manager.registry.create_version(
            application_id=application_id,
            tenant_id=req.tenant_id,
            version_str=req.version,
            configuration=req.configuration,
            composition_references=req.composition_references,
        )
        return ver.model_dump(mode="json")
    except ApplicationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{application_id}/promote")
def promote_version(
    application_id: str,
    req: PromoteVersionRequest,
    version_id: str = Query(...),
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    try:
        ver = manager.registry.promote_version(
            version_id=version_id,
            tenant_id=req.tenant_id,
            target_status=req.target_status,
        )
        return ver.model_dump(mode="json")
    except (ApplicationVersionNotFoundException, ApplicationNotFoundException) as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{application_id}/execute")
def execute_application(
    application_id: str,
    req: ExecuteApplicationRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    try:
        ctx = manager.runtime_manager.create_execution_context(
            tenant_id=req.tenant_id,
            application_id=application_id,
            application_version_id=req.version_id,
            identity_id=req.identity_id,
            environment=req.environment,
        )
        runtime = ApplicationRuntime(application_id, req.tenant_id)
        result = runtime.execute_pipeline(ctx, req.input_data)
        return result.model_dump(mode="json")
    except GovernanceBlockedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ExecutionCancelledException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{application_id}/cancel")
def cancel_execution(
    application_id: str,
    req: CancelExecutionRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    success = manager.runtime_manager.cancel_execution(req.execution_id, req.reason)
    if not success:
        raise HTTPException(status_code=404, detail=f"Execution '{req.execution_id}' not found or completed.")
    return {"status": "CANCELLED", "execution_id": req.execution_id}


@router.post("/{application_id}/interactions")
def add_interaction(
    application_id: str,
    req: CreateInteractionRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    turn = manager.interaction_manager.add_interaction(
        tenant_id=req.tenant_id,
        conversation_id=req.conversation_id,
        user_input=req.user_input,
        interaction_type=req.interaction_type,
    )
    return turn.model_dump(mode="json")


@router.get("/{application_id}/interactions")
def list_interactions(
    application_id: str,
    conversation_id: str = Query(...),
    tenant_id: str = Query("global"),
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    conv = manager.interaction_manager.get_conversation(tenant_id, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail=f"Conversation '{conversation_id}' not found.")
    return conv.model_dump(mode="json")


@router.post("/{application_id}/features")
def create_feature(
    application_id: str,
    req: CreateFeatureRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    flag = manager.feature_manager.create_flag(
        tenant_id=req.tenant_id,
        application_id=application_id,
        feature_key=req.feature_key,
        default_value=req.default_value,
    )
    return flag.model_dump(mode="json")


@router.post("/{application_id}/features/evaluate")
def evaluate_feature(
    application_id: str,
    req: EvaluateFeatureRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    res = manager.feature_manager.evaluate_feature(
        tenant_id=req.tenant_id,
        application_id=application_id,
        feature_key=req.feature_key,
        context=req.context,
    )
    return res


@router.post("/{application_id}/feedback")
def submit_feedback(
    application_id: str,
    req: SubmitFeedbackRequest,
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    fb = manager.feedback_manager.submit_feedback(
        tenant_id=req.tenant_id,
        application_id=application_id,
        execution_id=req.execution_id,
        feedback_type=req.feedback_type,
        score=req.score,
        comment=req.comment,
        corrected_output=req.corrected_output,
    )
    return fb.model_dump(mode="json")


@router.get("/{application_id}/analytics")
def get_analytics(
    application_id: str,
    tenant_id: str = Query("global"),
    manager: ApplicationPlatformManager = Depends(get_application_platform),
):
    rep = manager.analytics_engine.generate_report(tenant_id, application_id)
    return rep.model_dump(mode="json")
