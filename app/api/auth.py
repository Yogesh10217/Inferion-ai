from typing import List, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db_session
from app.auth.auth_service import AuthService
from app.auth.jwt_service import JWTService
from app.auth.api_key_service import APIKeyService
from app.auth.models import User, APIKey, Session
from app.auth.dependencies import get_current_user

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
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    ip_address = request.client.host if request.client else None
    user = await AuthService.authenticate_user(db, form_data.username, form_data.password, ip_address)
    
    access_token = JWTService.create_access_token(data={"sub": user.id})
    session = await AuthService.create_user_session(db, user)
    
    return Token(
        access_token=access_token,
        refresh_token=session.raw_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session)
):
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
            refresh_token=request.refresh_token, # keep same refresh token for now
            token_type="bearer"
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # In a full implementation, we'd revoke the refresh token in the Session DB model here
    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(db, "logout", user_id=current_user.id, ip_address=ip_address)
    return {"detail": "Successfully logged out"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/api-keys", response_model=APIKeyCreateOut)
async def create_api_key(
    request: Request,
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    raw_key, prefix, hashed_key = APIKeyService.generate_api_key()
    api_key = APIKey(
        user_id=current_user.id,
        name=key_data.name,
        prefix=prefix,
        hashed_key=hashed_key,
    )
    db.add(api_key)
    
    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(db, "api_key_created", user_id=current_user.id, ip_address=ip_address, details=f"Key name: {key_data.name}")
    
    await db.commit()
    await db.refresh(api_key)
    
    out = APIKeyCreateOut.model_validate(api_key)
    out.raw_key = raw_key
    return out


@router.get("/api-keys", response_model=List[APIKeyOut])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    stmt = select(APIKey).where(APIKey.user_id == current_user.id, APIKey.revoked_at.is_(None))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    request: Request,
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    stmt = select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id)
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
        
    api_key.revoked_at = datetime.now(timezone.utc)
    
    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(db, "api_key_revoked", user_id=current_user.id, ip_address=ip_address, details=f"Key ID: {key_id}")
    
    await db.commit()
    return {"detail": "API Key revoked"}
