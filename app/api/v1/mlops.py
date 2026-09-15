"""FastAPI Router for MLOps Platform (/v1/mlops/*)."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.mlops.manager import MLOpsManager
from app.mlops.registry import AIAssetType, AIAssetStatus
from app.mlops.deployment import DeploymentEnvironment, DeploymentStatus
from app.mlops.exceptions import MLOpsException

router = APIRouter(prefix="/v1/mlops", tags=["mlops"])

_global_mlops_manager = MLOpsManager()


def get_mlops() -> MLOpsManager:
    return _global_mlops_manager


# Schemas
class CreateAssetSchema(BaseModel):
    name: str
    asset_type: AIAssetType
    tenant_id: str = "global"
    description: str = ""
    initial_configuration: Dict[str, Any] = Field(default_factory=dict)


class CreateVersionSchema(BaseModel):
    version_number: str
    configuration: Dict[str, Any]
    creator: str = "system"
    changelog: str = ""


class CreateDeploymentSchema(BaseModel):
    name: str
    asset_id: str
    version_number: str
    environment: DeploymentEnvironment = DeploymentEnvironment.DEVELOPMENT
    tenant_id: str = "global"


class CreateReleaseSchema(BaseModel):
    name: str
    tenant_id: str = "global"
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)


class RollbackSchema(BaseModel):
    target_version_number: str
    reason: str = ""


# 1. Assets Endpoints
@router.post("/assets", status_code=status.HTTP_201_CREATED)
async def create_asset(data: CreateAssetSchema, mgr: MLOpsManager = Depends(get_mlops)):
    asset = mgr.registry.register_asset(
        name=data.name,
        asset_type=data.asset_type,
        tenant_id=data.tenant_id,
        description=data.description,
        initial_configuration=data.initial_configuration,
    )
    return {"status": "created", "asset": asset.model_dump()}


@router.get("/assets")
async def list_assets(tenant_id: Optional[str] = None, asset_type: Optional[AIAssetType] = None, mgr: MLOpsManager = Depends(get_mlops)):
    assets = mgr.registry.list_assets(tenant_id=tenant_id, asset_type=asset_type)
    return {"assets": [a.model_dump() for a in assets]}


@router.get("/assets/{id}")
async def get_asset(id: str, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        asset = mgr.registry.get_asset(id)
        return {"asset": asset.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/assets/{id}/versions", status_code=status.HTTP_201_CREATED)
async def create_asset_version(id: str, data: CreateVersionSchema, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        ver = mgr.registry.create_version(
            asset_id=id,
            version_number=data.version_number,
            configuration=data.configuration,
            creator=data.creator,
            changelog=data.changelog,
        )
        return {"status": "created", "version": ver.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/assets/{id}/versions")
async def list_asset_versions(id: str, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        asset = mgr.registry.get_asset(id)
        return {"versions": [v.model_dump() for v in asset.versions]}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# 2. Deployments Endpoints
@router.post("/deployments", status_code=status.HTTP_201_CREATED)
async def create_deployment(data: CreateDeploymentSchema, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        dep = mgr.deployment_manager.create_deployment(
            name=data.name,
            asset_id=data.asset_id,
            version_number=data.version_number,
            environment=data.environment,
            tenant_id=data.tenant_id,
        )
        return {"status": "created", "deployment": dep.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/deployments")
async def list_deployments(tenant_id: Optional[str] = None, environment: Optional[DeploymentEnvironment] = None, mgr: MLOpsManager = Depends(get_mlops)):
    deps = mgr.deployment_manager.list_deployments(tenant_id=tenant_id, environment=environment)
    return {"deployments": [d.model_dump() for d in deps]}


@router.get("/deployments/{id}")
async def get_deployment(id: str, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        dep = mgr.deployment_manager.get_deployment(id)
        return {"deployment": dep.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/deployments/{id}/approve")
async def approve_deployment(id: str, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        dep = mgr.deployment_manager.approve_deployment(id)
        return {"status": "approved", "deployment": dep.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/deployments/{id}/deploy")
async def execute_deployment(id: str, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        dep = mgr.deployment_manager.deploy(id)
        return {"status": "deployed", "deployment": dep.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/deployments/{id}/rollback")
async def rollback_deployment(id: str, data: RollbackSchema, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        plan = mgr.rollback_manager.create_rollback_plan(id, data.target_version_number, data.reason)
        res = mgr.rollback_manager.execute_rollback(plan)
        return {"status": "rolled_back", "result": res.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# 3. Releases Endpoints
@router.post("/releases", status_code=status.HTTP_201_CREATED)
async def create_release(data: CreateReleaseSchema, mgr: MLOpsManager = Depends(get_mlops)):
    rel = mgr.release_manager.create_release(name=data.name, tenant_id=data.tenant_id)
    return {"status": "created", "release": rel.model_dump()}


@router.post("/releases/{id}/validate")
async def validate_release(id: str, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        valid = mgr.release_manager.validate_release(id)
        return {"valid": valid, "release_id": id}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/releases/{id}/deploy")
async def deploy_release(id: str, mgr: MLOpsManager = Depends(get_mlops)):
    try:
        rel = mgr.release_manager.deploy_release(id)
        return {"status": "deployed", "release": rel.model_dump()}
    except MLOpsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# 4. Drift Endpoints
@router.get("/drift")
async def list_drift_events(deployment_id: Optional[str] = None, tenant_id: Optional[str] = None, mgr: MLOpsManager = Depends(get_mlops)):
    events = mgr.drift_detector.list_drift_events(deployment_id=deployment_id, tenant_id=tenant_id)
    return {"drift_events": [e.model_dump() for e in events]}


# 5. Fine-Tuning Pipeline Endpoints
@router.post("/fine-tuning/jobs")
async def create_fine_tuning_job(payload: Dict[str, Any]):
    from app.mlops.fine_tuning.job_service import FineTuningService
    service = FineTuningService()
    model = payload.get("model", "llama3.1")
    dataset_uri = payload.get("dataset_uri", "s3://datasets/train.jsonl")
    job = service.create_job(model=model, dataset_uri=dataset_uri, hyperparameters=payload.get("hyperparameters"))
    return job.model_dump()

