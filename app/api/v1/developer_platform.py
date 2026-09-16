"""REST API Router for Phase 5.21 Enterprise AI Developer Platform."""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.developer_platform.manager import DeveloperPlatformManager
from app.developer_platform.quality import QualityGate

router = APIRouter(prefix="/v1/developer-platform", tags=["developer-platform"])
_global_manager = DeveloperPlatformManager()


# DTOs
class CreateProjectRequestDTO(BaseModel):
    name: str
    description: str = ""
    repo_name: str = "main-repo"
    provider: str = "github"
    tenant_id: str = "global"


class RegisterAPIRequestDTO(BaseModel):
    name: str
    version: str = "1.0.0"
    tenant_id: str = "global"


class GenerateSDKRequestDTO(BaseModel):
    language: str = "python"
    service_id: str
    version: str = "1.0.0"
    tenant_id: str = "global"


class CreateWorkspaceRequestDTO(BaseModel):
    project_id: str
    developer_id: str
    tenant_id: str = "global"


class TriggerPipelineRequestDTO(BaseModel):
    project_id: str
    name: str
    tenant_id: str = "global"


class EvaluateQualityRequestDTO(BaseModel):
    min_coverage_pct: float = 80.0
    max_critical_bugs: int = 0
    coverage_pct: float
    critical_bugs: int


class AnalyzeDependenciesRequestDTO(BaseModel):
    dependencies: List[Dict[str, str]]
    tenant_id: str = "global"


# Endpoints
@router.get("/health")
def get_health():
    return {"status": "HEALTHY", "subsystem": "DeveloperPlatformManager", "version": "5.21.0"}


@router.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(req: CreateProjectRequestDTO):
    proj = _global_manager.create_project_with_repository(
        name=req.name,
        description=req.description,
        repo_name=req.repo_name,
        provider=req.provider,
        tenant_id=req.tenant_id,
    )
    return proj.model_dump()


@router.get("/projects")
def list_projects(tenant_id: Optional[str] = Query(None)):
    items = _global_manager.project_manager.list_projects(tenant_id=tenant_id)
    return [i.model_dump() for i in items]


@router.get("/projects/{project_id}")
def get_project(project_id: str):
    try:
        proj = _global_manager.project_manager.get_project(project_id)
        return proj.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/apis", status_code=status.HTTP_201_CREATED)
def register_api(req: RegisterAPIRequestDTO):
    svc = _global_manager.api_management_engine.register_api_service(name=req.name, version=req.version, tenant_id=req.tenant_id)
    return svc.model_dump()


@router.post("/sdk/generate", status_code=status.HTTP_201_CREATED)
def generate_sdk(req: GenerateSDKRequestDTO):
    sdk = _global_manager.sdk_manager.generate_sdk(language=req.language, service_id=req.service_id, version=req.version, tenant_id=req.tenant_id)
    return sdk.model_dump()


@router.post("/workspaces", status_code=status.HTTP_201_CREATED)
def create_workspace(req: CreateWorkspaceRequestDTO):
    ws = _global_manager.workspace_manager.create_workspace(project_id=req.project_id, developer_id=req.developer_id, tenant_id=req.tenant_id)
    return ws.model_dump()


@router.post("/pipelines", status_code=status.HTTP_201_CREATED)
def trigger_pipeline(req: TriggerPipelineRequestDTO):
    pipe = _global_manager.pipeline_manager.create_pipeline(project_id=req.project_id, name=req.name, tenant_id=req.tenant_id)
    run = _global_manager.pipeline_manager.trigger_pipeline_run(pipeline_id=pipe.pipeline_id, tenant_id=req.tenant_id)
    return run.model_dump()


@router.post("/quality/evaluate")
def evaluate_quality(req: EvaluateQualityRequestDTO):
    try:
        gate = QualityGate(name="API Gate", min_coverage_pct=req.min_coverage_pct, max_critical_bugs=req.max_critical_bugs)
        passed = _global_manager.quality_manager.evaluate_quality(gate, coverage_pct=req.coverage_pct, critical_bugs=req.critical_bugs)
        return {"status": "PASSED" if passed else "FAILED"}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/dependencies/analyze")
def analyze_dependencies(req: AnalyzeDependenciesRequestDTO):
    try:
        risks = _global_manager.dependency_manager.analyze_dependencies(req.dependencies, tenant_id=req.tenant_id)
        return [r.model_dump() for r in risks]
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/analytics")
def get_analytics(tenant_id: str = "global"):
    summary = _global_manager.analytics_engine.get_delivery_summary(tenant_id=tenant_id)
    return summary
