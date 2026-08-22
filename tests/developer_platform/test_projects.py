"""Unit tests for Developer Projects & Lifecycle state transitions."""

import pytest
from app.developer_platform.project import ProjectManager, ProjectLifecycle
from app.developer_platform.exceptions import InvalidProjectLifecycleTransition


def test_project_lifecycle_transitions():
    mgr = ProjectManager()
    proj = mgr.create_project(
        name="Customer Portal Extension",
        organization_id="org_1",
        workspace_id="ws_1",
        developer_id="dev_1",
    )
    assert proj.lifecycle == ProjectLifecycle.CREATED

    # Valid transitions CREATED -> DEVELOPMENT -> TESTING -> STAGED -> PUBLISHED
    mgr.transition_lifecycle(proj.project_id, ProjectLifecycle.DEVELOPMENT)
    mgr.transition_lifecycle(proj.project_id, ProjectLifecycle.TESTING)
    mgr.transition_lifecycle(proj.project_id, ProjectLifecycle.STAGED)
    p_pub = mgr.transition_lifecycle(proj.project_id, ProjectLifecycle.PUBLISHED)
    assert p_pub.lifecycle == ProjectLifecycle.PUBLISHED

    # Invalid transition PUBLISHED -> DEVELOPMENT raises error
    with pytest.raises(InvalidProjectLifecycleTransition):
        mgr.transition_lifecycle(proj.project_id, ProjectLifecycle.DEVELOPMENT)
