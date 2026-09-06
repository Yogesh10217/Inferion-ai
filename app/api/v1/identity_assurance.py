"""FastAPI REST API endpoints for Phase 5.48 Identity Assurance platform."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.identity_assurance.exceptions import (
    CrossTenantIdentityAssuranceException,
    IdentityAssuranceException,
    IdentityNotFoundException,
)
from app.identity_assurance.identities import IdentityType, IdentityCategory
from app.identity_assurance.manager import IdentityAssuranceManager

router = APIRouter(prefix="/v1/identities", tags=["Identity Assurance"])

_manager = IdentityAssuranceManager()


def get_manager() -> IdentityAssuranceManager:
    return _manager


class RegisterIdentityRequest(BaseModel):
    name: str
    identity_type: IdentityType = IdentityType.HUMAN
    category: IdentityCategory = IdentityCategory.EMPLOYEE
    external_id: Optional[str] = None


class AccessReviewRequest(BaseModel):
    title: str
    review_type: str = "PRIVILEGED_ACCESS"
    target_identities: List[str] = []


class InvestigationRequest(BaseModel):
    identity_id: str


class RemediationRequest(BaseModel):
    identity_id: str
    action_types: List[str] = ["REVOKE_UNUSED_ROLE"]


@router.post("", response_model=Dict[str, Any])
def register_identity(
    req: RegisterIdentityRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    identity = mgr.register_identity(
        tenant_id=x_tenant_id,
        name=req.name,
        identity_type=req.identity_type,
        category=req.category,
        external_id=req.external_id,
    )
    return identity.model_dump()


@router.get("/{identity_id}", response_model=Dict[str, Any])
def get_identity(
    identity_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    try:
        identity = mgr.get_identity(x_tenant_id, identity_id)
        return identity.model_dump()
    except CrossTenantIdentityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{identity_id}/profile", response_model=Dict[str, Any])
def get_profile(
    identity_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    try:
        profile = mgr.profile_manager.get_profile(x_tenant_id, identity_id)
        return profile.model_dump()
    except CrossTenantIdentityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{identity_id}/trust", response_model=Dict[str, Any])
def assess_trust(
    identity_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    try:
        assessment = mgr.trust_engine.assess_trust(x_tenant_id, identity_id)
        return assessment.model_dump()
    except CrossTenantIdentityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{identity_id}/privileges", response_model=Dict[str, Any])
def assess_privileges(
    identity_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    try:
        assessment = mgr.privilege_manager.assess_privileges(x_tenant_id, identity_id)
        return assessment.model_dump()
    except CrossTenantIdentityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{identity_id}/entitlements", response_model=Dict[str, Any])
def analyze_entitlements(
    identity_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    try:
        assessment = mgr.entitlement_manager.analyze_entitlements(x_tenant_id, identity_id)
        return assessment.model_dump()
    except CrossTenantIdentityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{identity_id}/risk", response_model=Dict[str, Any])
def get_risk(
    identity_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    try:
        assessment = mgr.risk_manager.assess_risk(x_tenant_id, identity_id)
        return assessment.model_dump()
    except CrossTenantIdentityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{identity_id}/assurance", response_model=Dict[str, Any])
def get_assurance(
    identity_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    try:
        score = mgr.evaluate_identity_assurance(x_tenant_id, identity_id)
        return score.model_dump()
    except CrossTenantIdentityAssuranceException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/access-reviews", response_model=Dict[str, Any])
def create_access_review(
    req: AccessReviewRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    review = mgr.access_review_manager.create_review(
        tenant_id=x_tenant_id,
        title=req.title,
        review_type=req.review_type,
        target_identities=req.target_identities,
    )
    return review.model_dump()


@router.get("/analytics", response_model=Dict[str, Any])
def get_analytics(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: IdentityAssuranceManager = Depends(get_manager),
):
    report = mgr.analytics_engine.generate_report(tenant_id=x_tenant_id)
    return report.model_dump()
