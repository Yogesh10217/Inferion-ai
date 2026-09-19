"""FastAPI Router for Data Fabric (/v1/data-sources, /v1/data-sync, /v1/data-catalog, /v1/data-governance)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.data_fabric.data_source import DataSourceStatus, DataSourceType
from app.data_fabric.exceptions import DataFabricException
from app.data_fabric.governance import DataClassification, DataPolicy
from app.data_fabric.manager import DataFabricManager
from app.data_fabric.sync import SyncStrategy

router = APIRouter(tags=["data-fabric"])

_global_fabric_manager = DataFabricManager()


def get_data_fabric() -> DataFabricManager:
    return _global_fabric_manager


# Schemas
class CreateDataSourceSchema(BaseModel):
    name: str
    source_type: DataSourceType
    connector_type: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    description: str = ""
    configuration: Dict[str, Any] = Field(default_factory=dict)
    secret_reference: Optional[str] = None


class UpdateDataSourceSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DataSourceStatus] = None
    configuration: Optional[Dict[str, Any]] = None


class CreateSyncJobSchema(BaseModel):
    strategy: SyncStrategy = SyncStrategy.FULL
    tenant_id: str = "global"
    idempotency_key: Optional[str] = None


class AccessCheckSchema(BaseModel):
    resource_id: str
    tenant_id: str = "global"
    classification: DataClassification = DataClassification.INTERNAL
    requester_id: str
    purpose: str = "AI Access"


# 1. Data Sources Endpoints
@router.post("/v1/data-sources", status_code=status.HTTP_201_CREATED)
async def create_data_source(data: CreateDataSourceSchema, mgr: DataFabricManager = Depends(get_data_fabric)):
    ds = mgr.source_manager.create_source(
        name=data.name,
        source_type=data.source_type,
        connector_type=data.connector_type,
        tenant_id=data.tenant_id,
        organization_id=data.organization_id,
        workspace_id=data.workspace_id,
        description=data.description,
        configuration=data.configuration,
        secret_reference=data.secret_reference,
    )
    return {"status": "created", "data_source": ds.model_dump()}


@router.get("/v1/data-sources")
async def list_data_sources(
    tenant_id: Optional[str] = None,
    source_type: Optional[DataSourceType] = None,
    mgr: DataFabricManager = Depends(get_data_fabric),
):
    sources = mgr.source_manager.list_sources(tenant_id=tenant_id, source_type=source_type)
    return {"data_sources": [s.model_dump() for s in sources]}


@router.get("/v1/data-sources/{id}")
async def get_data_source(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        ds = mgr.source_manager.get_source(id)
        return {"data_source": ds.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/v1/data-sources/{id}")
async def update_data_source(id: str, data: UpdateDataSourceSchema, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        ds = mgr.source_manager.update_source(id, **data.model_dump(exclude_unset=True))
        return {"status": "updated", "data_source": ds.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/v1/data-sources/{id}")
async def delete_data_source(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        mgr.source_manager.delete_source(id)
        return {"status": "deleted"}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/v1/data-sources/{id}/validate")
async def validate_data_source(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        ds = mgr.source_manager.get_source(id)
        conn = mgr.connector_factory.create_connector(ds)
        valid = await conn.validate()
        return {"valid": valid, "source_id": id}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/v1/data-sources/{id}/discover")
async def discover_data_source_schema(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        ds = mgr.source_manager.get_source(id)
        sch = await mgr.schema_engine.discover_schema(ds)
        return {"schema": sch.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/v1/data-sources/{id}/sync")
async def start_data_source_sync(id: str, data: CreateSyncJobSchema, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        job = mgr.sync_manager.create_sync_job(
            source_id=id, tenant_id=data.tenant_id, strategy=data.strategy, idempotency_key=data.idempotency_key
        )
        updated_job = await mgr.sync_manager.run_sync_job(job.job_id)
        return {"status": "started", "sync_job": updated_job.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# 2. Synchronization Endpoints
@router.get("/v1/data-sync/history")
async def list_sync_history(
    tenant_id: Optional[str] = None, source_id: Optional[str] = None, mgr: DataFabricManager = Depends(get_data_fabric)
):
    jobs = mgr.sync_manager.list_jobs(tenant_id=tenant_id, source_id=source_id)
    return {"sync_history": [j.model_dump() for j in jobs]}


@router.get("/v1/data-sync/{id}")
async def get_sync_job(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        job = mgr.sync_manager.get_sync_job(id)
        return {"sync_job": job.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/v1/data-sync/{id}/pause")
async def pause_sync_job(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        job = mgr.sync_manager.pause_sync_job(id)
        return {"sync_job": job.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/v1/data-sync/{id}/resume")
async def resume_sync_job(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        job = mgr.sync_manager.resume_sync_job(id)
        return {"sync_job": job.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/v1/data-sync/{id}/cancel")
async def cancel_sync_job(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        job = mgr.sync_manager.cancel_sync_job(id)
        return {"sync_job": job.model_dump()}
    except DataFabricException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# 3. Data Catalog Endpoints
@router.get("/v1/data-catalog")
async def list_catalog(
    tenant_id: Optional[str] = None,
    classification: Optional[str] = None,
    mgr: DataFabricManager = Depends(get_data_fabric),
):
    datasets = mgr.catalog.list_datasets(tenant_id=tenant_id, classification=classification)
    return {"datasets": [d.model_dump() for d in datasets]}


@router.get("/v1/data-catalog/{id}")
async def get_catalog_dataset(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    try:
        ds = mgr.catalog.get_dataset(id)
        return {"dataset": ds.model_dump()}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Dataset '{id}' not found in catalog")


@router.get("/v1/data-catalog/{id}/schema")
async def get_dataset_schema(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    sch = mgr.schema_engine.get_schema(id)
    return {"schema": sch.model_dump()}


@router.get("/v1/data-catalog/{id}/lineage")
async def get_dataset_lineage(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    upstream = mgr.lineage_manager.get_upstream_lineage(id)
    downstream = mgr.lineage_manager.get_downstream_lineage(id)
    return {"upstream": [u.model_dump() for u in upstream], "downstream": [d.model_dump() for d in downstream]}


@router.get("/v1/data-catalog/{id}/quality")
async def get_dataset_quality(id: str, mgr: DataFabricManager = Depends(get_data_fabric)):
    res = mgr.quality_engine.evaluate_quality(id, [])
    return {"quality": res.model_dump()}


# 4. Governance Endpoints
@router.get("/v1/data-governance/policies")
async def list_governance_policies(mgr: DataFabricManager = Depends(get_data_fabric)):
    return {"policies": [p.model_dump() for p in mgr.governance_engine._policies.values()]}


@router.post("/v1/data-governance/policies", status_code=status.HTTP_201_CREATED)
async def create_governance_policy(policy: DataPolicy, mgr: DataFabricManager = Depends(get_data_fabric)):
    pol = mgr.governance_engine.register_policy(policy)
    return {"status": "created", "policy": pol.model_dump()}


@router.post("/v1/data-governance/access-check")
async def check_data_access(data: AccessCheckSchema, mgr: DataFabricManager = Depends(get_data_fabric)):
    decision = mgr.governance_engine.evaluate_access(
        tenant_id=data.tenant_id,
        resource_id=data.resource_id,
        classification=data.classification,
        requester_id=data.requester_id,
        purpose=data.purpose,
    )
    return {"decision": decision.model_dump()}
