from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session_maker
from app.auth.models import User, APIKey
from app.tenant.models import Membership, WorkspaceMembership, Organization, Workspace

settings = get_settings()

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.auth_enabled:
            request.state.organization_id = None
            request.state.workspace_id = None
            return await call_next(request)

        auth_method = getattr(request.state, "auth_method", None)
        user_id = getattr(request.state, "user_id", None)
        
        if not user_id or auth_method in ["none", "public", "anonymous"]:
            request.state.organization_id = None
            request.state.workspace_id = None
            return await call_next(request)

        async with async_session_maker() as session:
            # If API Key, organization is hard-bound
            if auth_method == "api_key":
                api_key_id = getattr(request.state, "api_key_id", None)
                if api_key_id:
                    stmt = select(APIKey).where(APIKey.id == api_key_id)
                    result = await session.execute(stmt)
                    api_key = result.scalar_one_or_none()
                    if api_key:
                        request.state.organization_id = api_key.organization_id
                        request.state.workspace_id = api_key.workspace_id
                        return await call_next(request)
            
            # If JWT, resolve via header or default
            org_id_header = request.headers.get("X-Organization-Id")
            
            if org_id_header:
                org_id = org_id_header
            else:
                # Resolve default org
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if user and user.default_organization_id:
                    org_id = user.default_organization_id
                else:
                    # Check how many orgs user has
                    stmt = select(Membership).where(Membership.user_id == user_id)
                    result = await session.execute(stmt)
                    memberships = result.scalars().all()
                    if not memberships:
                        return JSONResponse(status_code=403, content={"detail": "User does not belong to any organization"})
                    if len(memberships) == 1:
                        org_id = memberships[0].organization_id
                    else:
                        return JSONResponse(status_code=400, content={"detail": "User belongs to multiple organizations. X-Organization-Id header is required."})

            # Verify membership
            stmt = select(Membership).where(Membership.organization_id == org_id, Membership.user_id == user_id)
            result = await session.execute(stmt)
            membership = result.scalar_one_or_none()
            if not membership or membership.status != "active":
                return JSONResponse(status_code=403, content={"detail": "Access to organization denied"})
                
            request.state.organization_id = org_id
            
            # Optional Workspace resolution
            workspace_id = request.headers.get("X-Workspace-Id")
            request.state.workspace_id = None
            if workspace_id:
                stmt = select(WorkspaceMembership).where(
                    WorkspaceMembership.workspace_id == workspace_id,
                    WorkspaceMembership.user_id == user_id
                )
                result = await session.execute(stmt)
                ws_membership = result.scalar_one_or_none()
                if not ws_membership:
                    return JSONResponse(status_code=403, content={"detail": "Access to workspace denied"})
                request.state.workspace_id = workspace_id
                
        return await call_next(request)
