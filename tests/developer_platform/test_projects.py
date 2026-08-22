"""Unit tests for ProjectManager."""

import pytest
from app.developer_platform.project import ProjectManager, ProjectStatus


def test_project_creation_and_listing():
    pm = ProjectManager()
    proj = pm.create_project("Inference Service", description="LLM inference project", tenant_id="t_proj")

    assert proj.name == "Inference Service"
    assert proj.status == ProjectStatus.ACTIVE

    items = pm.list_projects(tenant_id="t_proj")
    assert len(items) == 1
    assert items[0].project_id == proj.project_id
