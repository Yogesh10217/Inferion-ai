"""REST API Endpoints for Enterprise AI Data Governance Platform."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.data_governance.access import DataAccessRequest, DataAction, PrincipalType
from app.data_governance.assets import DataAssetOwner, DataAssetType, DataDomain
from app.data_governance.consent import ConsentPurpose
from app.data_governance.contracts import ContractSchema
from app.data_governance.manager import DataGovernanceManager
from app.data_governance.sharing import DataSharingScope

router = APIRouter(prefix="/v1/data-governance", tags=["data-governance"])

mgr = DataGovernanceManager()


class CreateAssetRequest(BaseModel):
    tenant_id: str = "global"
    name: str
    asset_type: DataAssetType = DataAssetType.DATASET
    owner_id: str = "system"
    owner_email: str = "admin@example.com"
    domain: DataDomain = DataDomain.GENERAL
    source_reference: Optional[Dict[str, Any]] = None
    content_sample: Optional[str] = None


class ClassifyAssetRequest(BaseModel):
    tenant_id: str = "global"
    content_sample: Optional[str] = None
    schema_fields: Optional[List[str]] = None


class EvaluateAccessApiRequest(BaseModel):
    tenant_id: str = "global"
    principal_id: str
    principal_type: PrincipalType = PrincipalType.USER
    asset_id: str
    action: DataAction = DataAction.READ
    purpose: ConsentPurpose = ConsentPurpose.AI_CONTEXT
    context: Dict[str, Any] = {}


class GrantConsentApiRequest(BaseModel):
    tenant_id: str = "global"
    subject_id: str
    purposes: List[ConsentPurpose] = [ConsentPurpose.AI_CONTEXT]
    allowed_asset_ids: Optional[List[str]] = None


class WithdrawConsentApiRequest(BaseModel):
    tenant_id: str = "global"
    idempotency_key: Optional[str] = None


class CreateContractApiRequest(BaseModel):
    tenant_id: str = "global"
    asset_id: str
    owner_id: str = "system"
    required_classification: str = "CONFIDENTIAL"


class ValidateContractApiRequest(BaseModel):
    tenant_id: str = "global"
    incoming_schema: Dict[str, str]


class CreateShareApiRequest(BaseModel):
    source_tenant_id: str = "tenant_a"
    target_tenant_id: str = "tenant_b"
    asset_id: str
    scope: DataSharingScope = DataSharingScope.CROSS_ORGANIZATION


class EvaluateRetentionApiRequest(BaseModel):
    tenant_id: str = "global"
    asset_id: str
    asset_age_days: int = 300


@router.post("/assets")
async def create_asset(req: CreateAssetRequest):
    try:
        owner = DataAssetOwner(owner_id=req.owner_id, owner_name=req.owner_id, owner_email=req.owner_email)
        res = mgr.register_and_govern_asset(
            tenant_id=req.tenant_id,
            name=req.name,
            asset_type=req.asset_type,
            owner=owner,
            domain=req.domain,
            source_reference=req.source_reference,
            content_sample=req.content_sample,
        )
        return res
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/assets")
async def list_assets(tenant_id: str = "global"):
    assets = mgr.asset_manager.list_assets(tenant_id=tenant_id)
    return {"assets": [a.model_dump() for a in assets]}


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str, tenant_id: str = "global"):
    try:
        asset = mgr.asset_manager.get_asset(asset_id, tenant_id)
        return asset.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/assets/{asset_id}/classify")
async def classify_asset(asset_id: str, req: ClassifyAssetRequest):
    res = mgr.classification_engine.classify_asset(
        tenant_id=req.tenant_id,
        asset_id=asset_id,
        content_sample=req.content_sample,
        schema_fields=req.schema_fields,
    )
    mgr.asset_manager.update_asset_classification(asset_id, req.tenant_id, res.assigned_level.name)
    return res.model_dump()


@router.post("/assets/{asset_id}/quality")
async def evaluate_quality(asset_id: str, tenant_id: str = "global"):
    res = mgr.quality_manager.evaluate_quality(
        tenant_id=tenant_id, asset_id=asset_id, sample_records=[{"id": "1", "data": "test"}]
    )
    return res.model_dump()


@router.get("/assets/{asset_id}/lineage")
async def get_lineage(asset_id: str, tenant_id: str = "global"):
    lineage = mgr.lineage_manager.get_asset_lineage(asset_id, tenant_id)
    return lineage.model_dump()


@router.post("/contracts")
async def create_contract(req: CreateContractApiRequest):
    spec = ContractSchema(required_classification=req.required_classification)
    c = mgr.contract_manager.create_contract(
        tenant_id=req.tenant_id,
        asset_id=req.asset_id,
        schema_spec=spec,
        owner_id=req.owner_id,
    )
    return c.model_dump()


@router.post("/contracts/{contract_id}/validate")
async def validate_contract(contract_id: str, req: ValidateContractApiRequest):
    contract = mgr.contract_manager._contracts.get(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    res = mgr.contract_manager.validate_producer_schema(
        tenant_id=req.tenant_id,
        asset_id=contract.asset_id,
        incoming_schema=req.incoming_schema,
    )
    return res.model_dump()


@router.post("/access/evaluate")
async def evaluate_access(req: EvaluateAccessApiRequest):
    access_req = DataAccessRequest(
        tenant_id=req.tenant_id,
        principal_id=req.principal_id,
        principal_type=req.principal_type,
        asset_id=req.asset_id,
        action=req.action,
        purpose=req.purpose,
        context=req.context,
    )
    decision = mgr.evaluate_access(access_req)
    return decision.model_dump()


@router.post("/consent")
async def grant_consent(req: GrantConsentApiRequest):
    consent = mgr.consent_manager.grant_consent(
        tenant_id=req.tenant_id,
        subject_id=req.subject_id,
        purposes=req.purposes,
        allowed_asset_ids=req.allowed_asset_ids,
    )
    return consent.model_dump()


@router.post("/consent/{subject_id}/withdraw")
async def withdraw_consent(subject_id: str, req: WithdrawConsentApiRequest):
    consent = mgr.consent_manager.withdraw_consent(
        tenant_id=req.tenant_id,
        subject_id=subject_id,
        idempotency_key=req.idempotency_key,
    )
    return consent.model_dump()


@router.post("/shares")
async def request_share(req: CreateShareApiRequest):
    ag = mgr.sharing_manager.request_cross_tenant_share(
        source_tenant_id=req.source_tenant_id,
        target_tenant_id=req.target_tenant_id,
        asset_id=req.asset_id,
        scope=req.scope,
    )
    return ag.model_dump()


@router.post("/retention/evaluate")
async def evaluate_retention(req: EvaluateRetentionApiRequest):
    eval_res = mgr.retention_manager.evaluate_retention(
        tenant_id=req.tenant_id,
        asset_id=req.asset_id,
        asset_age_days=req.asset_age_days,
    )
    return eval_res.model_dump()


@router.get("/trust/{asset_id}")
async def get_trust(asset_id: str, tenant_id: str = "global"):
    score = mgr.trust_engine.get_trust_score(asset_id, tenant_id)
    return score.model_dump()


@router.get("/analytics")
async def get_analytics(tenant_id: str = "global"):
    report = mgr.analytics_engine.generate_report(tenant_id)
    return report.model_dump()
