"""REST API Router for Enterprise AI Lifecycle Platform (Phase 5.33)."""

from typing import Any, Dict

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.ai_lifecycle_platform.agents import AgentAutonomyLevel, AgentType
from app.ai_lifecycle_platform.assets import AIAssetType
from app.ai_lifecycle_platform.datasets import DatasetClassification
from app.ai_lifecycle_platform.drift import DriftSeverity, DriftType
from app.ai_lifecycle_platform.gates import GateType
from app.ai_lifecycle_platform.manager import AILifecyclePlatformManager
from app.ai_lifecycle_platform.models import ModelFramework, ModelType
from app.ai_lifecycle_platform.promotion import PromotionTarget
from app.ai_lifecycle_platform.releases import ReleaseRisk
from app.ai_lifecycle_platform.retirement import RetirementReason

router = APIRouter(prefix="/ai-lifecycle", tags=["ai-lifecycle"])
mgr = AILifecyclePlatformManager()


class AssetRegisterRequest(BaseModel):
    name: str
    asset_type: AIAssetType = AIAssetType.MODEL
    description: str = ""


class DatasetRegisterRequest(BaseModel):
    name: str
    classification: DatasetClassification = DatasetClassification.INTERNAL


class ModelRegisterRequest(BaseModel):
    name: str
    model_type: ModelType = ModelType.LLM
    framework: ModelFramework = ModelFramework.TRANSFORMERS


class AgentRegisterRequest(BaseModel):
    name: str
    agent_type: AgentType = AgentType.TASK_AGENT
    autonomy_level: AgentAutonomyLevel = AgentAutonomyLevel.HUMAN_APPROVED


class EvaluationRunRequest(BaseModel):
    target_asset_id: str
    suite_id: str
    overall_passed: bool = True


class GateCreateRequest(BaseModel):
    name: str
    gate_type: GateType = GateType.SECURITY
    is_hard_gate: bool = True


class PromotionRequestModel(BaseModel):
    asset_id: str
    target: PromotionTarget = PromotionTarget.STAGING
    is_high_risk: bool = False


class ReleaseCreateRequest(BaseModel):
    title: str
    asset_id: str
    version: str = "1.0.0"
    risk_level: ReleaseRisk = ReleaseRisk.MEDIUM


class DriftDetectRequest(BaseModel):
    asset_id: str
    drift_type: DriftType = DriftType.PERFORMANCE_DRIFT
    severity: DriftSeverity = DriftSeverity.HIGH


class RollbackRequestModel(BaseModel):
    asset_id: str
    target_version: str = "1.0.0"
    reason: str = "Performance degradation"


class RetirementRequestModel(BaseModel):
    asset_id: str
    reason: RetirementReason = RetirementReason.DEPRECATED


@router.post("/assets", response_model=Dict[str, Any])
async def register_asset(
    req: AssetRegisterRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    asset = mgr.asset_manager.register_asset(tenant_id, req.name, req.asset_type, req.description)
    return asset.model_dump()


@router.post("/datasets", response_model=Dict[str, Any])
async def register_dataset(
    req: DatasetRegisterRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    ds = mgr.dataset_manager.register_dataset(tenant_id, req.name, req.classification)
    return ds.model_dump()


@router.post("/models", response_model=Dict[str, Any])
async def register_model(
    req: ModelRegisterRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    mdl = mgr.model_manager.register_model(tenant_id, req.name, req.model_type, req.framework)
    return mdl.model_dump()


@router.post("/agents", response_model=Dict[str, Any])
async def register_agent(
    req: AgentRegisterRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    ag = mgr.agent_manager.register_agent(tenant_id, req.name, req.agent_type, req.autonomy_level)
    return ag.model_dump()


@router.post("/evaluations", response_model=Dict[str, Any])
async def run_evaluation(
    req: EvaluationRunRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    run = mgr.evaluation_manager.run_evaluation(tenant_id, req.target_asset_id, req.suite_id, req.overall_passed)
    return run.model_dump()


@router.post("/gates", response_model=Dict[str, Any])
async def create_gate(
    req: GateCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    gate = mgr.gate_manager.create_gate(tenant_id, req.name, req.gate_type, req.is_hard_gate)
    return gate.model_dump()


@router.post("/promotions", response_model=Dict[str, Any])
async def request_promotion(
    req: PromotionRequestModel,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    prom = mgr.promotion_manager.request_promotion(tenant_id, req.asset_id, req.target, is_high_risk=req.is_high_risk)
    return prom.model_dump()


@router.post("/releases", response_model=Dict[str, Any])
async def create_release(
    req: ReleaseCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rel = mgr.release_manager.create_release(tenant_id, req.title, req.asset_id, req.version, req.risk_level)
    return rel.model_dump()


@router.post("/drift", response_model=Dict[str, Any])
async def detect_drift(
    req: DriftDetectRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    drift = mgr.drift_manager.detect_drift(tenant_id, req.asset_id, req.drift_type, req.severity)
    return drift.model_dump()


@router.post("/rollbacks", response_model=Dict[str, Any])
async def request_rollback(
    req: RollbackRequestModel,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rbreq = mgr.rollback_manager.request_rollback(tenant_id, req.asset_id, req.target_version, req.reason)
    return rbreq.model_dump()


@router.post("/retirement", response_model=Dict[str, Any])
async def request_retirement(
    req: RetirementRequestModel,
    tenant_id: str = Query(..., description="Tenant ID"),
):
    ret = mgr.retirement_manager.request_retirement(tenant_id, req.asset_id, req.reason)
    return ret.model_dump()


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics_report(
    tenant_id: str = Query(..., description="Tenant ID"),
):
    rep = mgr.analytics_engine.generate_report(tenant_id=tenant_id)
    return rep.model_dump()
