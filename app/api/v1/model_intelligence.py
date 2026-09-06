"""REST API Endpoints for Model Intelligence Platform (Phase 5.44)."""

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.model_intelligence.manager import ModelIntelligenceManager
from app.model_intelligence.exceptions import ModelIntelligenceException, CrossTenantModelIntelligenceException

router = APIRouter(prefix="/v1/models", tags=["model-intelligence"])
model_intel_manager = ModelIntelligenceManager()


class ModelRegistrationRequest(BaseModel):
    name: str
    model_type: str = "LLM"
    provider_name: str = "InternalProvider"


class EvaluationRequest(BaseModel):
    model_id: str
    version_tag: str = "1.0.0"
    eval_type: str = "DETERMINISTIC"


@router.post("/register", response_model=Dict[str, Any])
def register_model(req: ModelRegistrationRequest, x_tenant_id: str = Header(default="global")):
    ref = model_intel_manager.registry.register_model(
        name=req.name,
        tenant_id=x_tenant_id,
        model_type=req.model_type,
        provider={"provider_id": "p-1", "provider_name": req.provider_name},
    )
    return {"status": "SUCCESS", "model": ref.dict()}


@router.get("/", response_model=Dict[str, Any])
def list_models(x_tenant_id: str = Header(default="global")):
    models = model_intel_manager.registry.list_models(tenant_id=x_tenant_id)
    return {"models": [m.dict() for m in models]}


@router.get("/{model_id}", response_model=Dict[str, Any])
def get_model(model_id: str, x_tenant_id: str = Header(default="global")):
    try:
        model = model_intel_manager.registry.get_model(model_id=model_id, tenant_id=x_tenant_id)
        return {"model": model.dict()}
    except CrossTenantModelIntelligenceException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ModelIntelligenceException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/evaluate", response_model=Dict[str, Any])
def evaluate_model(req: EvaluationRequest, x_tenant_id: str = Header(default="global")):
    eval_res = model_intel_manager.evaluation_manager.create_evaluation(
        model_id=req.model_id,
        tenant_id=x_tenant_id,
        version_tag=req.version_tag,
        eval_type=req.eval_type,
        metrics=[{"name": "accuracy", "score": 0.92, "passed": True}],
    )
    return {"evaluation": eval_res.dict()}


@router.get("/{model_id}/trust", response_model=Dict[str, Any])
def assess_trust(model_id: str, x_tenant_id: str = Header(default="global")):
    try:
        trust = model_intel_manager.trust_engine.calculate_trust(
            model_id=model_id,
            tenant_id=x_tenant_id,
            factors=[{"dimension": "QUALITY", "score": 90.0, "weight": 1.0}],
        )
        return {"trust_assessment": trust.dict()}
    except CrossTenantModelIntelligenceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{model_id}/assurance", response_model=Dict[str, Any])
def assess_assurance(model_id: str, x_tenant_id: str = Header(default="global")):
    try:
        assurance = model_intel_manager.assurance_manager.compute_assurance(
            model_id=model_id,
            tenant_id=x_tenant_id,
            scores=[{"dimension": "PERFORMANCE", "score": 0.95, "weight": 1.0, "passed": True}],
        )
        return {"assurance": assurance.dict()}
    except CrossTenantModelIntelligenceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/analytics/summary", response_model=Dict[str, Any])
def get_analytics_summary(x_tenant_id: str = Header(default="global")):
    report = model_intel_manager.analytics_engine.generate_report(tenant_id=x_tenant_id)
    return {"analytics": report.dict()}
