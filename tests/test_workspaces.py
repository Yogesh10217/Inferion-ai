import pytest

from app.admin.exceptions import ResourceNotFoundException
from app.admin.organization_service import OrganizationAdminService
from app.admin.workspace_service import WorkspaceAdminService
from app.core.database import async_session_maker


@pytest.mark.asyncio
async def test_workspace_crud_lifecycle():
    async with async_session_maker() as db:
        org_service = OrganizationAdminService(db)
        ws_service = WorkspaceAdminService(db)

        # 1. Create Parent Organization
        org = await org_service.create_organization(name="Workspace Test Org", slug="ws-test-org")

        # 2. Create Workspace
        ws = await ws_service.create_workspace(
            name="Production Workspace",
            organization_id=org.id,
            slug="prod-ws",
            description="Production environments workspace",
        )
        assert ws.id is not None
        assert ws.name == "Production Workspace"
        assert ws.organization_id == org.id

        # 3. Get Workspace
        fetched = await ws_service.get_workspace(ws.id)
        assert fetched is not None
        assert fetched.name == "Production Workspace"

        # 4. List Workspaces for Org
        workspaces = await ws_service.list_workspaces(organization_id=org.id)
        assert len(workspaces) >= 1
        assert any(w.id == ws.id for w in workspaces)

        # 5. Update Workspace
        updated = await ws_service.update_workspace(ws.id, name="Renamed Workspace")
        assert updated.name == "Renamed Workspace"


@pytest.mark.asyncio
async def test_workspace_not_found():
    async with async_session_maker() as db:
        ws_service = WorkspaceAdminService(db)
        with pytest.raises(ResourceNotFoundException):
            await ws_service.get_workspace("non_existent_workspace_999")
