"""FastAPI REST API Router for Phase 5.17 Identity, Access & Zero-Trust Platform."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.identity.authentication import AuthenticationMethod
from app.identity.identity import IdentityType
from app.identity.manager import IdentitySecurityManager
from app.identity.privileged_access import PrivilegedRole

router = APIRouter(prefix="/v1/identity", tags=["Identity Platform"])

_global_identity = IdentitySecurityManager()


def get_identity_manager() -> IdentitySecurityManager:
    return _global_identity


class CreateIdentityRequest(BaseModel):
    username: str
    identity_type: IdentityType = IdentityType.HUMAN
    tenant_id: str = "global"
    roles: List[str] = Field(default_factory=lambda: ["viewer"])


class AuthenticateRequest(BaseModel):
    identity_id: str
    method: AuthenticationMethod = AuthenticationMethod.JWT
    tenant_id: str = "global"
    mfa_verified: bool = False


class RequestJITAccessRequest(BaseModel):
    identity_id: str
    role: PrivilegedRole = PrivilegedRole.TENANT_ADMIN
    tenant_id: str = "global"
    duration_minutes: int = 60


class EvaluateZeroTrustRequest(BaseModel):
    identity_id: str
    tenant_id: str = "global"
    network_trusted: bool = True
    device_trusted: bool = True
    risk_score: float = 0.0


@router.get("/health", status_code=status.HTTP_200_OK)
def identity_health():
    return {"status": "HEALTHY", "subsystem": "Identity Platform", "phase": "5.17"}


@router.post("/identities", status_code=status.HTTP_201_CREATED)
def create_identity(
    req: CreateIdentityRequest,
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    ident = mgr.identity_manager.create_identity(
        username=req.username,
        identity_type=req.identity_type,
        tenant_id=req.tenant_id,
        roles=req.roles,
    )
    return ident.model_dump()


@router.get("/identities", status_code=status.HTTP_200_OK)
def list_identities(
    tenant_id: Optional[str] = Query(None),
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    return {"identities": [i.model_dump() for i in mgr.identity_manager.list_identities(tenant_id)]}


@router.post("/authenticate", status_code=status.HTTP_200_OK)
def authenticate(
    req: AuthenticateRequest,
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    res = mgr.auth_manager.authenticate(
        identity_id=req.identity_id,
        method=req.method,
        tenant_id=req.tenant_id,
        mfa_verified=req.mfa_verified,
    )
    mgr.metrics_collector.record_authentication(req.tenant_id, res.is_authenticated)
    return res.model_dump()


@router.post("/privileged-access/request", status_code=status.HTTP_201_CREATED)
def request_privileged_access(
    req: RequestJITAccessRequest,
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    grant = mgr.privileged_access_manager.request_privileged_access(
        identity_id=req.identity_id,
        role=req.role,
        tenant_id=req.tenant_id,
        duration_minutes=req.duration_minutes,
    )
    return grant.model_dump()


@router.post("/zero-trust/evaluate", status_code=status.HTTP_200_OK)
def evaluate_zero_trust(
    req: EvaluateZeroTrustRequest,
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    eval_res = mgr.zero_trust_engine.evaluate(
        identity_id=req.identity_id,
        tenant_id=req.tenant_id,
        network_trusted=req.network_trusted,
        device_trusted=req.device_trusted,
        risk_score=req.risk_score,
    )
    return eval_res.model_dump()


@router.get("/sessions", status_code=status.HTTP_200_OK)
def list_sessions(
    tenant_id: Optional[str] = Query(None),
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    return {"sessions": [s.model_dump() for s in mgr.session_manager.list_sessions(tenant_id)]}


@router.post("/sessions/{session_id}/revoke", status_code=status.HTTP_200_OK)
def revoke_session(
    session_id: str,
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    try:
        sess = mgr.session_manager.revoke_session(session_id)
        return sess.model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/audit", status_code=status.HTTP_200_OK)
def list_audit_events(
    tenant_id: Optional[str] = Query(None),
    mgr: IdentitySecurityManager = Depends(get_identity_manager),
):
    return {"events": [e.model_dump() for e in mgr.audit_manager.list_events(tenant_id)]}
