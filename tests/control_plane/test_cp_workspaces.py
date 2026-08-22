"""Unit tests for WorkspaceManager."""

import pytest
from app.control_plane.workspace import WorkspaceManager, WorkspaceEnvironment
from app.control_plane.exceptions import WorkspaceNotFoundException


def test_workspace_crud_and_archiving():
    mgr = WorkspaceManager()
    ws = mgr.create_workspace(
        name="Prod AI Sandbox",
        organization_id="org_123",
        tenant_id="tenant_y",
        environment=WorkspaceEnvironment.PRODUCTION,
    )
    assert ws.environment == WorkspaceEnvironment.PRODUCTION

    # Archive
    archived = mgr.archive_workspace(ws.workspace_id)
    assert archived.is_archived is True

    # Delete
    mgr.delete_workspace(ws.workspace_id)
    with pytest.raises(WorkspaceNotFoundException):
        mgr.get_workspace(ws.workspace_id)
