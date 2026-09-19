from datetime import datetime, timezone
from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_service import APIKeyService
from app.auth.auth_service import AuthService
from app.auth.dependencies import get_current_user
from app.auth.jwt_service import JWTService
from app.auth.models import APIKey, User
from app.core.database import get_db_session

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    is_admin: bool

    model_config = {"from_attributes": True}


class APIKeyCreate(BaseModel):
    name: str


class APIKeyOut(BaseModel):
    id: str
    name: str
    prefix: str
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class APIKeyCreateOut(APIKeyOut):
    raw_key: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=Token)
async def login(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)
):
    ip_address = request.client.host if request.client else None
    user = await AuthService.authenticate_user(db, form_data.username, form_data.password, ip_address)

    org_id = user.default_organization_id
    if not org_id:
        from app.tenant.models import Membership

        stmt_mem = select(Membership).where(Membership.user_id == user.id)
        res_mem = await db.execute(stmt_mem)
        mem = res_mem.scalars().first()
        if not mem:
            raise HTTPException(status_code=403, detail="User does not belong to any organization")
        org_id = mem.organization_id

    access_token = JWTService.create_access_token(data={"sub": user.id})
    session = await AuthService.create_user_session(db, user, organization_id=org_id)

    return Token(access_token=access_token, refresh_token=session.raw_token, token_type="bearer")  # nosec B106


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db_session)):
    try:
        payload = JWTService.verify_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

        user_id = payload.get("sub")
        # In a real app we'd verify the refresh_token_hash matches a valid session in DB
        # For brevity here we just issue a new access token if the refresh token is valid and unexpired
        access_token = JWTService.create_access_token(data={"sub": user_id})
        return Token(
            access_token=access_token,
            refresh_token=request.refresh_token,  # keep same refresh token for now
            token_type="bearer",  # nosec B106
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/logout")
async def logout(
    request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)
):
    # Assuming we revoke via session. For now just audit log.
    org_id = getattr(request.state, "organization_id", "SYSTEM")
    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db, "logout", organization_id=org_id, actor_id=current_user.id, ip_address=ip_address
    )
    return {"detail": "Successfully logged out"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/api-keys", response_model=APIKeyCreateOut)
async def create_api_key(
    request: Request,
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    org_id = getattr(request.state, "organization_id", None)
    ws_id = getattr(request.state, "workspace_id", None)
    if not org_id:
        raise HTTPException(status_code=403, detail="Organization context required to create API key")

    raw_key, prefix, hashed_key = APIKeyService.generate_api_key()
    api_key = APIKey(
        user_id=current_user.id,
        organization_id=org_id,
        workspace_id=ws_id,
        name=key_data.name,
        prefix=prefix,
        hashed_key=hashed_key,
    )
    db.add(api_key)

    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db,
        "api_key_created",
        organization_id=org_id,
        workspace_id=ws_id,
        actor_id=current_user.id,
        resource_type="APIKey",
        ip_address=ip_address,
        details=f"Key name: {key_data.name}",
    )

    await db.commit()
    await db.refresh(api_key)

    out = APIKeyCreateOut.model_validate(api_key)
    out.raw_key = raw_key
    return out


@router.get("/api-keys", response_model=List[APIKeyOut])
async def list_api_keys(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)):
    stmt = select(APIKey).where(APIKey.user_id == current_user.id, APIKey.revoked_at.is_(None))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    request: Request,
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    stmt = select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id)
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    api_key.revoked_at = datetime.now(timezone.utc)

    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db,
        "api_key_revoked",
        organization_id=api_key.organization_id,
        workspace_id=api_key.workspace_id,
        actor_id=current_user.id,
        resource_type="APIKey",
        resource_id=api_key.id,
        ip_address=ip_address,
    )

    await db.commit()
    return {"detail": "API Key revoked"}


@router.get("/sso/authorize")
async def sso_authorize(provider_id: str = "google", state: str = "state-token"):
    from app.sso.oidc import get_oidc_manager

    manager = get_oidc_manager()
    try:
        url = manager.generate_authorize_url(provider_id=provider_id, state=state)
        return {"authorization_url": url, "provider_id": provider_id, "state": state}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sso/callback")
async def sso_callback(
    code: str, state: Optional[str] = None, provider_id: str = "google", db: AsyncSession = Depends(get_db_session)
):
    from app.sso.oidc import get_oidc_manager

    manager = get_oidc_manager()
    # Mock token exchange for OIDC flow testing
    mock_id_token = jwt.encode(
        {"sub": "sso-user-123", "email": "sso@example.com", "name": "SSO User", "groups": ["Admins"]},
        "secret",
        algorithm="HS256",
    )
    session_data = manager.process_id_token(provider_id=provider_id, id_token=mock_id_token)

    access_token = JWTService.create_access_token(
        data={"sub": session_data.sub, "email": session_data.email, "role": session_data.role}
    )
    refresh_token = JWTService.create_refresh_token(data={"sub": session_data.sub})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",  # nosec B105
        "user": session_data.model_dump(),
    }
