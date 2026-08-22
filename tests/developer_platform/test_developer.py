"""Unit tests for Developer registration, verification, permissions, and lifecycle."""

import pytest
from app.developer_platform.developer import DeveloperManager, DeveloperStatus
from app.developer_platform.exceptions import DeveloperNotFoundException, DeveloperPermissionDeniedException


def test_developer_registration_and_verification():
    mgr = DeveloperManager()

    dev = mgr.register_developer(
        user_id="user_100",
        full_name="Jane Doe",
        email="jane@example.com",
        tenant_id="tenant_dev",
        auto_activate=False,
    )
    assert dev.status == DeveloperStatus.PENDING

    verified = mgr.verify_developer(dev.developer_id)
    assert verified.status == DeveloperStatus.ACTIVE
    assert verified.verified_at is not None


def test_developer_permission_enforcement():
    mgr = DeveloperManager()
    dev = mgr.register_developer(user_id="u1", full_name="John", email="john@example.com", auto_activate=True)

    assert mgr.validate_permission(dev.developer_id, "build_extensions") is True

    mgr.suspend_developer(dev.developer_id, reason="Security review")

    with pytest.raises(DeveloperPermissionDeniedException):
        mgr.validate_permission(dev.developer_id, "build_extensions")
