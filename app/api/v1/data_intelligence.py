"""FastAPI Router for Enterprise AI Data Intelligence Platform (Phase 5.43)."""

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data_intelligence.exceptions import (
    CrossTenantDataIntelligenceException,
    DatasetNotFoundException,
)
from app.data_intelligence.manager import DataIntelligenceManager

router = APIRouter(prefix="/data", tags=["Data Intelligence"])
_mgr = DataIntelligenceManager()


class DatasetCreateRequest(BaseModel):
    name: str
    tenant_id: str = "global"
    dataset_type: str = "TABLE"
    source_id: Optional[str] = None


class QualityEvalRequest(BaseModel):
    dataset_id: str
    tenant_id: str = "global"
    observations: Optional[Dict[str, float]] = None


class AnomalyDetectRequest(BaseModel):
    dataset_id: str
    tenant_id: str = "global"
    metric_name: str
    expected_value: float
    actual_value: float
    anomaly_type: str = "UNUSUAL_VOLUME"
    severity: str = "HIGH"


class IncidentCreateRequest(BaseModel):
    dataset_id: str
    tenant_id: str = "global"
    title: str
    severity: str = "P2_HIGH"
    anomaly_id: Optional[str] = None


class RemediationPlanRequest(BaseModel):
    incident_id: str
    dataset_id: str
    tenant_id: str = "global"
    action_type: str = "PIPELINE_RESTART"
    target_subsystem: str = "orchestration"


@router.post("/datasets")
async def register_dataset(req: DatasetCreateRequest):
    ds = _mgr.dataset_manager.register_dataset(
        name=req.name,
        tenant_id=req.tenant_id,
        source_id=req.source_id,
    )
    return ds.model_dump()


@router.get("/datasets")
async def list_datasets(tenant_id: str = "global"):
    datasets = _mgr.dataset_manager.list_datasets(tenant_id)
    return [d.model_dump() for d in datasets]


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, tenant_id: str = "global"):
    try:
        ds = _mgr.dataset_manager.get_dataset(dataset_id, tenant_id)
        return ds.model_dump()
    except CrossTenantDataIntelligenceException:
        raise HTTPException(status_code=403, detail="Access denied.")
    except DatasetNotFoundException:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found.")


@router.get("/sources")
async def list_sources(tenant_id: str = "global"):
    sources = _mgr.source_manager.list_sources(tenant_id)
    return [s.model_dump() for s in sources]


@router.post("/profiling")
async def profile_dataset(dataset_id: str, tenant_id: str = "global"):
    prof = _mgr.profiling_manager.profile_dataset(dataset_id, tenant_id)
    return prof.model_dump()


@router.post("/quality/evaluate")
async def evaluate_quality(req: QualityEvalRequest):
    res = _mgr.quality_manager.evaluate_quality(req.dataset_id, req.tenant_id)
    return res.model_dump()


@router.post("/validation")
async def validate_data(dataset_id: str, tenant_id: str = "global"):
    res = _mgr.validation_manager.validate_data(dataset_id, tenant_id)
    return res.model_dump()


@router.post("/anomalies")
async def detect_anomaly(req: AnomalyDetectRequest):
    from app.data_intelligence.anomalies import DataAnomalySeverity, DataAnomalyType

    anom = _mgr.anomaly_manager.detect_anomaly(
        dataset_id=req.dataset_id,
        tenant_id=req.tenant_id,
        anomaly_type=DataAnomalyType(req.anomaly_type),
        severity=DataAnomalySeverity(req.severity),
        metric_name=req.metric_name,
        expected_value=req.expected_value,
        actual_value=req.actual_value,
    )
    return anom.model_dump()


@router.get("/anomalies")
async def list_anomalies(tenant_id: str = "global"):
    anomalies = _mgr.anomaly_manager.list_anomalies(tenant_id)
    return [a.model_dump() for a in anomalies]


@router.get("/drift")
async def evaluate_drift(dataset_id: str, tenant_id: str = "global"):
    ass = _mgr.drift_manager.evaluate_drift_assessment(dataset_id, tenant_id)
    return ass.model_dump()


@router.get("/freshness")
async def evaluate_freshness(dataset_id: str, tenant_id: str = "global"):
    ass = _mgr.freshness_manager.evaluate_freshness(dataset_id, tenant_id)
    return ass.model_dump()


@router.get("/lineage")
async def get_lineage(tenant_id: str = "global"):
    lin = _mgr.lineage_manager.get_lineage(tenant_id)
    return lin.model_dump()


@router.get("/schema")
async def get_schema(dataset_id: str, tenant_id: str = "global"):
    ds = _mgr.schema_manager._schemas.get(dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Schema not found.")
    return ds.model_dump()


@router.get("/pipelines")
async def list_pipelines(tenant_id: str = "global"):
    pipes = [p for p in _mgr.pipeline_manager._pipelines.values() if p.tenant_id == tenant_id]
    return [p.model_dump() for p in pipes]


@router.post("/incidents")
async def create_incident(req: IncidentCreateRequest):
    from app.data_intelligence.incidents import DataIncidentSeverity

    inc = _mgr.incident_manager.create_incident(
        dataset_id=req.dataset_id,
        tenant_id=req.tenant_id,
        title=req.title,
        severity=DataIncidentSeverity(req.severity),
        anomaly_id=req.anomaly_id,
    )
    return inc.model_dump()


@router.get("/incidents")
async def list_incidents(tenant_id: str = "global"):
    incs = _mgr.incident_manager.list_incidents(tenant_id)
    return [i.model_dump() for i in incs]


@router.get("/investigations")
async def list_investigations(tenant_id: str = "global"):
    invs = [i for i in _mgr.investigation_manager._investigations.values() if i.tenant_id == tenant_id]
    return [i.model_dump() for i in invs]


@router.post("/remediation")
async def create_remediation(req: RemediationPlanRequest):
    from app.data_intelligence.remediation import DataRemediationAction, DataRemediationPriority

    plan = _mgr.remediation_manager.create_remediation_plan(
        incident_id=req.incident_id,
        dataset_id=req.dataset_id,
        tenant_id=req.tenant_id,
        priority=DataRemediationPriority.P2_HIGH,
        actions=[
            DataRemediationAction(action_id="act-1", action_type=req.action_type, target_subsystem=req.target_subsystem)
        ],
    )
    return plan.model_dump()


@router.get("/trust")
async def evaluate_trust(dataset_id: str, tenant_id: str = "global"):
    ass = _mgr.trust_engine.evaluate_trust(dataset_id, tenant_id)
    return ass.model_dump()


@router.get("/analytics")
async def get_analytics(tenant_id: str = "global"):
    rpt = _mgr.analytics_engine.generate_report(tenant_id)
    return rpt.model_dump()
