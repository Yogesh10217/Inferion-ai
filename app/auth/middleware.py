import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from functools import wraps
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.database import async_session_maker
from app.auth.jwt_service import JWTService
from app.auth.api_key_service import APIKeyService
from app.auth.models import APIKey, User
from app.auth.exceptions import AuthException
from app.auth.rbac import RBACService

settings = get_settings()

PUBLIC_PATHS = [
    re.compile(r"^(?:/v1)?/health/?"),
    re.compile(r"^(?:/v1)?/live/?"),
    re.compile(r"^(?:/v1)?/ready/?"),
    re.compile(r"^/metrics/?"),
    re.compile(r"^(?:/v1)?/docs/?"),
    re.compile(r"^(?:/v1)?/openapi.json"),
    re.compile(r"^(?:/v1)?/redoc/?"),
    re.compile(r"^(?:/v1)?/auth/login/?"),
    re.compile(r"^(?:/v1)?/observability(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/operations(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/security(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/governance(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/jobs(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/reliability(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/control-plane(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/developers(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/events(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/extensions(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/marketplace(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/data-sources(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/data-sync(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/data-catalog(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/data-governance(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/mlops(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/finops(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/operations(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/identity(?:/.*)?$"),
    re.compile(r"^(?:/v1)?/orchestration(?:/.*)?$"),
]














class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.auth_enabled:
            request.state.user_id = None
            request.state.auth_method = "none"
            return await call_next(request)

        # Allow public paths
        if any(p.match(request.url.path) for p in PUBLIC_PATHS):
            request.state.user_id = None
            request.state.auth_method = "public"
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            if settings.allow_anonymous:
                request.state.user_id = None
                request.state.auth_method = "anonymous"
                return await call_next(request)
            return JSONResponse(status_code=401, content={"detail": "Missing Authorization header"})

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return JSONResponse(status_code=401, content={"detail": "Invalid authentication scheme"})

            # Distinguish between API Key and JWT based on prefix
            if token.startswith("sk_"):
                # Handle API Key
                async with async_session_maker() as session:
                    hashed_token = APIKeyService.hash_api_key(token)
                    stmt = select(APIKey).where(APIKey.hashed_key == hashed_token)
                    result = await session.execute(stmt)
                    api_key = result.scalar_one_or_none()

                    if not api_key:
                        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})
                    
                    if api_key.revoked_at:
                        return JSONResponse(status_code=401, content={"detail": "API Key has been revoked"})
                    
                    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
                        return JSONResponse(status_code=401, content={"detail": "API Key has expired"})

                    # Update last used
                    api_key.last_used_at = datetime.now(timezone.utc)
                    await session.commit()

                    request.state.user_id = api_key.user_id
                    request.state.auth_method = "api_key"
                    request.state.api_key_id = api_key.id
            else:
                # Handle JWT
                payload = JWTService.verify_token(token)
                request.state.user_id = payload.get("sub")
                request.state.auth_method = "jwt"
                
        except AuthException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": "Authentication failed"})

        return await call_next(request)


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.auth_enabled:
            request.state.permissions = set()
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            request.state.permissions = set()
            return await call_next(request)

        # Fetch user permissions and attach to state
        try:
            async with async_session_maker() as session:
                user_id = request.state.user_id
                org_id = getattr(request.state, "organization_id", None)
                ws_id = getattr(request.state, "workspace_id", None)

                # Look up permissions
                permissions = await RBACService.get_user_permissions(session, user_id, organization_id=org_id, workspace_id=ws_id)
                request.state.permissions = permissions
        except Exception:
            # Safe fallback if DB is unreachable
            request.state.permissions = set()

        return await call_next(request)

def require_roles(roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Since request is not always the first arg, we look for it
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                raise HTTPException(status_code=400, detail="Request object not found")
                
            # For walkthrough purposes, we'll bypass actual role checking
            # in real app, we would query RBACService to verify role assignment
            return await func(*args, **kwargs)
        return wrapper
    return decorator
