"""Unit tests for WorkspaceManager."""

import pytest
from app.developer_platform.development_workspaces import WorkspaceManager


def test_workspace_creation_and_credential_session():
    wm = WorkspaceManager()
    ws = wm.create_workspace(project_id="p101", developer_id="dev_alice", tenant_id="t_ws")

    assert ws.project_id == "p101"
    assert ws.status == "READY"
    assert len(wm._sessions) == 1
