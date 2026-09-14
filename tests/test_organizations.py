import pytest
from app.core.database import async_session_maker
from app.admin.organization_service import OrganizationAdminService
from app.admin.exceptions import ResourceNotFoundException, InvalidOperationException


@pytest.mark.asyncio
async def test_organization_crud_lifecycle():
    async with async_session_maker() as db:
        service = OrganizationAdminService(db)

        # 1. Create Organization
        org = await service.create_organization(
            name="Acme Corp",
            slug="acme-corp",
        )
        assert org.id is not None
        assert org.name == "Acme Corp"
        assert org.slug == "acme-corp"
        assert org.status == "active"

        # 2. Get Organization by ID
        fetched = await service.get_organization(org.id)
        assert fetched is not None
        assert fetched.id == org.id

        # 3. List Organizations
        orgs = await service.list_organizations(limit=10)
        assert len(orgs) >= 1
        assert any(o.id == org.id for o in orgs)

        # 4. Suspend Organization
        suspended = await service.suspend_organization(org.id, actor_id="admin_user")
        assert suspended.status == "suspended"

        # 5. Reactivate Organization
        reactivated = await service.reactivate_organization(org.id)
        assert reactivated.status == "active"


@pytest.mark.asyncio
async def test_organization_not_found():
    async with async_session_maker() as db:
        service = OrganizationAdminService(db)
        with pytest.raises(ResourceNotFoundException):
            await service.get_organization("non_existent_org_id_12345")


@pytest.mark.asyncio
async def test_create_duplicate_slug():
    async with async_session_maker() as db:
        service = OrganizationAdminService(db)
        await service.create_organization(name="Unique Org 1", slug="unique-slug-test")

        with pytest.raises(Exception):
            await service.create_organization(name="Unique Org 2", slug="unique-slug-test")
