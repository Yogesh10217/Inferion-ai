from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_service import AuthService
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.database import get_db_session
from app.tenant.models import Membership, Organization
from app.tenant.schemas import OrganizationCreate, OrganizationResponse, OrganizationUpdate

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org_in: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    request: Request = None,
):
    # Check if slug exists
    stmt = select(Organization).where(Organization.slug == org_in.slug)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Organization slug already exists")

    org = Organization(name=org_in.name, slug=org_in.slug)
    db.add(org)
    await db.flush()

    # Assign creator as Owner (Assuming we have a mechanism to fetch OWNER role_id; for now, stub)
    # Ideally, we look up the Owner role ID from the DB
    from app.auth.models import Role
    stmt_role = select(Role).where(Role.name == "Admin")  # Or 'Owner'
    res_role = await db.execute(stmt_role)
    owner_role = res_role.scalars().first()
    role_id = owner_role.id if owner_role else "stub-role-id"

    membership = Membership(
        organization_id=org.id,
        user_id=current_user.id,
        role_id=role_id,
        status="active"
    )
    db.add(membership)

    ip_address = request.client.host if request and request.client else None
    await AuthService.log_audit_event(
        db, "organization_created",
        organization_id=org.id,
        actor_id=current_user.id,
        resource_type="Organization",
        resource_id=org.id,
        ip_address=ip_address
    )

    await db.commit()
    await db.refresh(org)
    return org


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Only return organizations the user is a member of, or all if user is system admin
    if current_user.is_admin:
        stmt = select(Organization)
    else:
        stmt = (
            select(Organization)
            .join(Membership, Organization.id == Membership.organization_id)
            .where(Membership.user_id == current_user.id)
        )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Must be member or system admin
    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not current_user.is_admin:
        stmt_mem = select(Membership).where(Membership.organization_id == org_id, Membership.user_id == current_user.id)
        res_mem = await db.execute(stmt_mem)
        if not res_mem.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not a member of this organization")

    return org


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_in: OrganizationUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Enforce active org matches org_id or user is system admin
    req_org_id = getattr(request.state, "organization_id", None)
    if not current_user.is_admin and req_org_id != org_id:
        raise HTTPException(status_code=403, detail="Must be in the organization's context to update it")

    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if org_in.name is not None:
        org.name = org_in.name
    if org_in.slug is not None:
        # Check slug collision
        stmt_slug = select(Organization).where(Organization.slug == org_in.slug, Organization.id != org_id)
        res_slug = await db.execute(stmt_slug)
        if res_slug.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Slug already in use")
        org.slug = org_in.slug

    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db, "organization_updated",
        organization_id=org.id,
        actor_id=current_user.id,
        resource_type="Organization",
        resource_id=org.id,
        ip_address=ip_address
    )

    await db.commit()
    await db.refresh(org)
    return org


@router.delete("/{org_id}", status_code=204)
async def delete_organization(
    org_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Enforce system admin for hard deletion, or org owner
    # For now, require system admin for safety
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only system admins can delete organizations")

    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    await db.delete(org)

    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db, "organization_deleted",
        organization_id=org.id,
        actor_id=current_user.id,
        resource_type="Organization",
        resource_id=org.id,
        ip_address=ip_address
    )

    await db.commit()
